"""
mcp_permission_demo.py
一个最小可运行的 MCP 权限控制演示：
- 认证 (Bearer token)
- Scope 校验
- RBAC 动态工具可见性
- ABAC 上下文条件判断

运行：
    pip install fastapi uvicorn pydantic
    python mcp_permission_demo.py

测试：
    curl -H "Authorization: Bearer role_admin_env_prod" http://localhost:8000/tools
    curl -X POST -H "Authorization: Bearer role_admin_env_prod" \
         -H "Content-Type: application/json" \
         -d '{"tool":"shell_exec","arguments":{"command":"ls"}}' \
         http://localhost:8000/invoke
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Callable, Any

app = FastAPI(title="MCP Permission Control Demo")
security = HTTPBearer(auto_error=False)


# ===================== 1. 认证与 AccessToken 模型 =====================

class AccessToken(BaseModel):
    subject: str
    roles: list[str]
    scopes: list[str]
    env: str = "dev"
    department: Optional[str] = None


def mock_verify_token(bearer: str) -> AccessToken:
    """
    模拟 OAuth token 解析。
    生产环境应替换为 JWT 签名/aud/exp/scope 校验，或调用授权服务器 introspection endpoint。
    """
    parts = bearer.lower().split("_")

    role = "user"
    if "admin" in parts:
        role = "admin"
    elif "manager" in parts:
        role = "manager"

    env = "prod" if "prod" in parts else "dev"

    scopes = ["mcp:tools:read"]
    if role in ("manager", "admin"):
        scopes.append("mcp:tools:write")
    if role == "admin":
        scopes.append("mcp:tools:admin")

    return AccessToken(
        subject=f"user-{role}",
        roles=[role],
        scopes=scopes,
        env=env,
        department="engineering",
    )


async def get_access(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AccessToken:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    token = credentials.credentials
    # 兼容 "Bearer xxx" 与纯 token
    if token.startswith("Bearer "):
        token = token[7:]
    return mock_verify_token(token)


# ===================== 2. RBAC 策略 =====================

RBAC_POLICY = {
    "user": {
        "read_file": ["read"],
        "search_web": ["search"],
    },
    "manager": {
        "read_file": ["read"],
        "send_email": ["send"],
    },
    "admin": "*",
}


def has_rbac_access(access: AccessToken, tool_name: str, action: str = "use") -> bool:
    if "admin" in access.roles:
        return True
    for role in access.roles:
        perms = RBAC_POLICY.get(role, {})
        if perms == "*":
            return True
        if tool_name in perms and action in perms[tool_name]:
            return True
    return False


# ===================== 3. ABAC 上下文判断 =====================

def abac_check(
    access: AccessToken,
    tool_name: str,
    arguments: dict,
    context: dict,
) -> bool:
    """
    基于属性/上下文的访问控制。
    规则示例：
    1. 包含未信任输入时，禁止调用高风险工具。
    2. shell_exec 仅限 admin，或 engineering 部门的 manager，且必须在 prod 环境。
    3. send_email 收件人超过 10 个时仅 admin 允许。
    """
    if context.get("contains_untrusted_input") and tool_name in {"shell_exec", "send_email"}:
        return False

    if tool_name == "shell_exec":
        if access.env != "prod":
            return False
        if "admin" in access.roles:
            return True
        if "manager" in access.roles and access.department == "engineering":
            return True
        return False

    if tool_name == "send_email":
        recipients = arguments.get("to", [])
        if isinstance(recipients, list) and len(recipients) > 10 and "admin" not in access.roles:
            return False

    return True


# ===================== 4. 工具注册中心 =====================

class ToolRegistry:
    def __init__(self):
        self.tools: dict[str, dict] = {}

    def register(
        self,
        name: str,
        description: str,
        risk: str = "low",
        required_scope: str = "mcp:tools:read",
    ):
        def decorator(fn: Callable) -> Callable:
            self.tools[name] = {
                "name": name,
                "description": description,
                "risk": risk,
                "required_scope": required_scope,
                "handler": fn,
            }
            return fn
        return decorator

    def list_allowed(self, access: AccessToken, context: dict) -> list[dict]:
        """动态工具可见性：只返回当前用户有权限且 ABAC 通过的工具。"""
        visible = []
        for name, meta in self.tools.items():
            if not has_rbac_access(access, name):
                continue
            if meta["required_scope"] not in access.scopes:
                continue
            if not abac_check(access, name, {}, context):
                continue
            visible.append({
                "name": name,
                "description": meta["description"],
                "risk": meta["risk"],
                "required_scope": meta["required_scope"],
            })
        return visible

    async def invoke(
        self,
        access: AccessToken,
        tool_name: str,
        arguments: dict,
        context: dict,
    ) -> Any:
        if tool_name not in self.tools:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")

        meta = self.tools[tool_name]

        # 执行前再次校验：RBAC + Scope + ABAC
        if not has_rbac_access(access, tool_name):
            raise HTTPException(status_code=403, detail="RBAC denied")
        if meta["required_scope"] not in access.scopes:
            raise HTTPException(status_code=403, detail="Scope denied")
        if not abac_check(access, tool_name, arguments, context):
            raise HTTPException(status_code=403, detail="ABAC denied")

        return await meta["handler"](arguments)


registry = ToolRegistry()


# ===================== 5. 示例工具 =====================

@registry.register("read_file", "读取工作目录下的文件", risk="low", required_scope="mcp:tools:read")
async def read_file(args: dict) -> dict:
    path = args.get("path", "/workspace/demo.txt")
    return {"status": "success", "action": "read", "path": path}


@registry.register("send_email", "发送邮件给指定收件人", risk="medium", required_scope="mcp:tools:write")
async def send_email(args: dict) -> dict:
    return {
        "status": "success",
        "action": "send_email",
        "to": args.get("to"),
        "subject": args.get("subject"),
    }


@registry.register("shell_exec", "执行 shell 命令（高风险）", risk="high", required_scope="mcp:tools:admin")
async def shell_exec(args: dict) -> dict:
    cmd = args.get("command", "")
    return {"status": "success", "action": "shell", "command": cmd, "output": f"Mock output for: {cmd}"}


# ===================== 6. HTTP 接口 =====================

class InvokeRequest(BaseModel):
    tool: str
    arguments: dict = Field(default_factory=dict)


def build_context(request: Request) -> dict:
    return {"contains_untrusted_input": request.headers.get("X-Untrusted-Input") == "true"}


@app.get("/tools")
async def list_tools(request: Request, access: AccessToken = Depends(get_access)):
    """返回当前用户可见的工具列表。"""
    return {"tools": registry.list_allowed(access, build_context(request))}


@app.post("/invoke")
async def invoke_tool(
    req: InvokeRequest,
    request: Request,
    access: AccessToken = Depends(get_access),
):
    """执行工具调用，调用前进行完整的权限校验。"""
    result = await registry.invoke(access, req.tool, req.arguments, build_context(request))
    return {"result": result}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

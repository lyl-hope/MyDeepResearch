import subprocess
from typing import List,Optional
from langchain.agents.middleware import DockerExecutionPolicy

class DockerMountExecutionPolicy(DockerExecutionPolicy):
    """
    自定义 DockerExecutionPolicy：挂载本地目录到容器，
    并设置工作目录为 container_workspace。
    """

    def __init__(
        self,
        host_workspace: str,
        container_workspace: str = "/workspace",
        **kwargs
    ):
        """
        host_workspace: 需要挂载的本机目录路径
        container_workspace: 容器内挂载路径
        kwargs: 传给父类的 DockerExecutionPolicy 参数
        """
        super().__init__(**kwargs)
        self.host_workspace = host_workspace
        self.container_workspace = container_workspace

    def build_docker_run_args(self) -> List[str]:
        """
        重写 Docker 启动参数
        """
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # 父类默认的 run 参数（image、timeout 等）
        args = super().build_docker_run_args()

        # 正确拼接 volume 挂载
        # rw 可读写
        mount_arg = f"{self.host_workspace}:{self.container_workspace}:rw"

        # 先加挂载参数
        args.extend(["-v", mount_arg])

        # 容器内默认工作目录
        args.extend(["-w", self.container_workspace])
        print("!!!!!!")
        return args
    def run(self, command: str, timeout: Optional[float] = None) -> str:
        """
        覆盖父类 run 方法，保证挂载和工作目录生效
        """
        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{self.host_workspace}:{self.container_workspace}:rw",
            "-w", self.container_workspace,
            self.image,
            "bash", "-c", command
        ]
        print("Docker 命令：", " ".join(docker_cmd))  # 测试用，确保能打印
        try:
            return subprocess.check_output(docker_cmd, stderr=subprocess.STDOUT, timeout=timeout or self.command_timeout, text=True).strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker command failed: {e.output}") from e

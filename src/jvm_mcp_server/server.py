"""JVM MCP Server实现"""

import json
import time
from typing import List, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .arthas import ArthasClient

class JvmMcpServer:
    """JVM MCP服务器"""
    def __init__(self, name: str = "arthas-jvm-monitor"):
        self.name = name
        self.mcp = FastMCP(name)
        self.arthas = ArthasClient()
        self._setup_tools()
        self._setup_prompts()

    def _setup_tools(self):
        """设置MCP工具"""
        @self.mcp.tool()
        def list_java_processes() -> List[Dict[str, str]]:
            """列出所有Java进程"""
            output = self.arthas.list_java_processes()
            processes = []
            for line in output.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        processes.append({
                            "pid": parts[0],
                            "name": parts[1],
                            "args": " ".join(parts[2:]) if len(parts) > 2 else ""
                        })
            return processes

        @self.mcp.tool()
        def get_thread_info(pid: int) -> Dict:
            """获取指定进程的线程信息"""
            output = self.arthas.get_thread_info(pid)
            return {
                "raw_output": output,
                "timestamp": time.time()
            }

        @self.mcp.tool()
        def get_jvm_info(pid: int) -> Dict:
            """获取JVM基础信息"""
            output = self.arthas.get_jvm_info(pid)
            return {
                "raw_output": output,
                "timestamp": time.time()
            }

        @self.mcp.tool()
        def get_memory_info(pid: int) -> Dict:
            """获取内存使用情况"""
            output = self.arthas.get_memory_info(pid)
            return {
                "raw_output": output,
                "timestamp": time.time()
            }

        @self.mcp.tool()
        def get_stack_trace(pid: int, thread_name: str) -> Dict:
            """获取指定线程的堆栈信息"""
            output = self.arthas.get_stack_trace(pid, thread_name)
            return {
                "raw_output": output,
                "timestamp": time.time()
            }

        @self.mcp.tool()
        def get_class_info(pid: int, class_pattern: str) -> Dict:
            """获取类信息"""
            output = self.arthas.get_class_info(pid, class_pattern)
            return {
                "raw_output": output,
                "timestamp": time.time()
            }

        @self.mcp.tool()
        def get_jvm_status(pid: int) -> Dict:
            """获取JVM整体状态报告
            
            Args:
                pid: 可选的进程ID，如果不指定则自动选择第一个非arthas的Java进程
            
            Returns:
                包含JVM状态信息的字典
            """
            if pid is None:
                # 如果没有指定PID，获取第一个非arthas的Java进程
                processes = list_java_processes()
                for process in processes:
                    if "arthas" not in process["name"].lower():
                        pid = int(process["pid"])
                        break
                if pid is None:
                    return {"error": "No valid Java process found"}

            thread_info = get_thread_info(pid)
            jvm_info = get_jvm_info(pid)
            memory_info = get_memory_info(pid)
            
            return {
                "pid": pid,
                "thread_info": thread_info,
                "jvm_info": jvm_info,
                "memory_info": memory_info,
                "timestamp": time.time()
            }

    def _setup_prompts(self):
        """设置MCP提示"""
        @self.mcp.prompt()
        def jvm_analysis_prompt(status: Dict) -> str:
            """创建JVM分析提示"""
            
            return f"""你是一位经验丰富的Java性能调优专家，
            请考虑以下方面：
            1. JVM整体健康状况
            2. 内存使用情况和潜在的内存问题
            3. 线程状态和可能的死锁
            4. 性能优化建议
            5. 需要关注的警告信息

            请提供详细的分析报告和具体的优化建议。
            """

    def run(self):
        """运行服务器"""
        print(f"Starting {self.name}...")
        self.mcp.run() 
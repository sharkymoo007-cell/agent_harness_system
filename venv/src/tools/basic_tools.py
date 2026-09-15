import os
from datetime import datetime
from simpleeval import simple_eval
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """math operation calculation. example: '(100 - 32) / 1.8'。"""
    try:
        result = simple_eval(expression)
        return f"Result is: {result}"
    except Exception as e:
        return f"Error[calculation error]: {str(e)}"

@tool
def write_file(filename: str, content: str) -> str:
    """writes content into file, autocreation if undefined, when naming a autocreated file, in addition to its name, add a time stamp and a agent signiture"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        return f"write success: {filename}"
    except Exception as e:
        return f"write FAILED: {str(e)}"

@tool
def read_file(filename: str) -> str:
    """reads content from file"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"read FAILED: {str(e)}"

@tool
def list_dir(path: str = ".") -> str:
    """Lists all files and directories in the specified local directory path. Default is current directory '.'"""
    try:
        files = os.listdir(path)
        if not files:
            return "Directory is empty."
        return "Files in directory:\n" + "\n".join([f"- {f}" for f in files])
    except Exception as e:
        return f"list_dir FAILED: {str(e)}"

@tool
def system_clock() -> str:
    """returns the current time from year to seconds of the system"""
    try:
        return f"The current system time in day/month/year, hour/minute/second is {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}"
    except Exception as e:
        return f"system_clock FAILED: {str(e)}"

@tool
def create_directory(new_directory: str = "./agent_creations/new_directory") -> str:
    """create new directory under the 'agent_creations' directory"""
    try:
        os.mkdir(new_directory)
        return f"New directory created at: {new_directory}"
    except Exception as e:
        return f"create_directory FAILED: {str(e)}"

@tool
def delete_file(filename: str) -> str:
    """delete specified file"""
    try:
        os.remove(filename)
        return f"File {filename} has been deleted successfully"
    except Exception as e:
        return f"delete_file FAILED: {str(e)}"

@tool
def delete_directory(directory: str) -> str:
    """delete specified directory"""
    try:
        os.removedirs(directory)
        return f"Directory {directory} has been removed successfully"
    except Exception as e:
        return f"delete_directory FAILED: {str(e)}"
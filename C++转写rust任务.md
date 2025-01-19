
参考项目：
https://github.com/adamhlt/DLL-Injector/blob/main/Source/DLL%20Injector/DLL_Injector.cpp

AI:
使用Poe自带的Cluade-3.5-Opus。
完整聊天: https://poe.com/s/ddgEdVaW62OPW42KHozi

测试说明（用管理员打开cmd）：
.\dll_injector.exe .\testdll.dll Notepad.exe


### Round-1: 生成基本代码
**ASK:**
以下是一段运行在windows平台的C++代码，请使用rust语言重新实现等价功能，并提供项目配置：
```
#include <Windows.h>
#include <TlHelp32.h>
#include <iostream>

/**
 * Function wich find the process id of the specified process.
 * \param lpProcessName : name of the target process.
 * \return : the process id if the process is found else -1.
 */
DWORD GetProcessByName(const char* lpProcessName)
{
    char lpCurrentProcessName[255];

    PROCESSENTRY32 ProcList {};
    ProcList.dwSize = sizeof(ProcList);

    const HANDLE hProcList = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcList == INVALID_HANDLE_VALUE)
        return -1;

    if (!Process32First(hProcList, &ProcList))
        return -1;

    wcstombs_s(nullptr, lpCurrentProcessName, ProcList.szExeFile, 255);

    if (lstrcmpA(lpCurrentProcessName, lpProcessName) == 0)
        return ProcList.th32ProcessID;

    while (Process32Next(hProcList, &ProcList))
    {
        wcstombs_s(nullptr, lpCurrentProcessName, ProcList.szExeFile, 255);

        if (lstrcmpA(lpCurrentProcessName, lpProcessName) == 0)
            return ProcList.th32ProcessID;
    }

    return -1;
}

int main(const int argc, char* argv[])
{
    char* lpDLLName;
    char* lpProcessName;
    char lpFullDLLPath[MAX_PATH];

    if (argc == 3)
    {
        lpDLLName = argv[1];
        lpProcessName = argv[2];
    }
    else
    {
        printf("[HELP] inject.exe <dll> <process>\n");
        return -1;
    }

    const DWORD dwProcessID = GetProcessByName(lpProcessName);
    if (dwProcessID == (DWORD) -1)
    {
        printf("An error is occured when trying to find the target process.\n");
        return -1;
    }

    printf("[DLL Injector]\n");
    printf("Process : %s\n", lpProcessName);
    printf("Process ID : %i\n\n", (int)dwProcessID);

    const DWORD dwFullPathResult = GetFullPathNameA(lpDLLName, MAX_PATH, lpFullDLLPath, nullptr);
    if (dwFullPathResult == 0)
    {
        printf("An error is occured when trying to get the full path of the DLL.\n");
        return -1;
    }

    const HANDLE hTargetProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwProcessID);
    if (hTargetProcess == INVALID_HANDLE_VALUE)
    {
        printf("An error is occured when trying to open the target process.\n");
        return -1;
    }

    printf("[PROCESS INJECTION]\n");
    printf("Process opened successfully.\n");

    const LPVOID lpPathAddress = VirtualAllocEx(hTargetProcess, nullptr, lstrlenA(lpFullDLLPath) + 1, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (lpPathAddress == nullptr)
    {
        printf("An error is occured when trying to allocate memory in the target process.\n");
        return -1;
    }

    printf("Memory allocate at 0x%llx\n", (uintptr_t)lpPathAddress);

    const DWORD dwWriteResult = WriteProcessMemory(hTargetProcess, lpPathAddress, lpFullDLLPath, lstrlenA(lpFullDLLPath) + 1, nullptr);
    if (dwWriteResult == 0)
    {
        printf("An error is occured when trying to write the DLL path in the target process.\n");
        return -1;
    }

    printf("DLL path writen successfully: %s.\n", lpFullDLLPath);

    const HMODULE hModule = GetModuleHandleA("kernel32.dll");
    if (hModule == INVALID_HANDLE_VALUE || hModule == nullptr)
        return -1;

    const FARPROC lpFunctionAddress = GetProcAddress(hModule, "LoadLibraryA");
    if (lpFunctionAddress == nullptr)
    {
        printf("An error is occured when trying to get \"LoadLibraryA\" address.\n");
        return -1;
    }

    printf("LoadLibraryA address at 0x%llx\n", (uintptr_t)lpFunctionAddress);

    const HANDLE hThreadCreationResult = CreateRemoteThread(hTargetProcess, nullptr, 0, (LPTHREAD_START_ROUTINE)lpFunctionAddress, lpPathAddress, 0, nullptr);
    if (hThreadCreationResult == INVALID_HANDLE_VALUE)
    {
        printf("An error is occured when trying to create the thread in the target process.\n");
        return -1;
    }

    printf("DLL Injected !\n");

    return 0;
}
```


**ANS:**
以下是使用Rust语言实现的等价功能代码，包括项目配置：
```
// main.rs
use std::env;
use std::ffi::CString;
use std::mem;
use std::os::raw::c_void;
use std::ptr;
use winapi::shared::minwindef::{DWORD, FALSE, LPVOID};
use winapi::um::handleapi::CloseHandle;
use winapi::um::libloaderapi::{GetModuleHandleA, GetProcAddress};
use winapi::um::memoryapi::{VirtualAllocEx, WriteProcessMemory};
use winapi::um::processthreadsapi::{CreateRemoteThread, OpenProcess};
use winapi::um::tlhelp32::{
    CreateToolhelp32Snapshot, Process32First, Process32Next, PROCESSENTRY32, TH32CS_SNAPPROCESS,
};
use winapi::um::winnt::{MEM_COMMIT, MEM_RESERVE, PAGE_EXECUTE_READWRITE, PROCESS_ALL_ACCESS};

fn get_process_by_name(process_name: &str) -> Option<DWORD> {
    let snapshot = unsafe { CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0) };
    if snapshot == ptr::null_mut() {
        return None;
    }

    let mut process_entry: PROCESSENTRY32 = unsafe { mem::zeroed() };
    process_entry.dwSize = mem::size_of::<PROCESSENTRY32>() as u32;

    if unsafe { Process32First(snapshot, &mut process_entry) } == 0 {
        return None;
    }

    loop {
        let current_process_name =
            unsafe { CString::from_raw(process_entry.szExeFile.as_ptr() as *mut i8) };
        if current_process_name.to_str().unwrap() == process_name {
            return Some(process_entry.th32ProcessID);
        }

        if unsafe { Process32Next(snapshot, &mut process_entry) } == 0 {
            break;
        }
    }

    None
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        println!("[HELP] inject.exe <dll> <process>");
        return;
    }

    let dll_name = &args[1];
    let process_name = &args[2];

    let process_id = match get_process_by_name(process_name) {
        Some(pid) => pid,
        None => {
            println!("An error occurred when trying to find the target process.");
            return;
        }
    };

    println!("[DLL Injector]");
    println!("Process: {}", process_name);
    println!("Process ID: {}\n", process_id);

    let full_dll_path = match std::fs::canonicalize(dll_name) {
        Ok(path) => path,
        Err(_) => {
            println!("An error occurred when trying to get the full path of the DLL.");
            return;
        }
    };

    let target_process = unsafe { OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id) };
    if target_process.is_null() {
        println!("An error occurred when trying to open the target process.");
        return;
    }

    println!("[PROCESS INJECTION]");
    println!("Process opened successfully.");

    let path_address = unsafe {
        VirtualAllocEx(
            target_process,
            ptr::null_mut(),
            full_dll_path.to_str().unwrap().len() + 1,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_EXECUTE_READWRITE,
        )
    };
    if path_address.is_null() {
        println!("An error occurred when trying to allocate memory in the target process.");
        return;
    }

    println!("Memory allocated at 0x{:x}", path_address as usize);

    let dll_path_cstring = CString::new(full_dll_path.to_str().unwrap()).unwrap();
    let write_result = unsafe {
        WriteProcessMemory(
            target_process,
            path_address,
            dll_path_cstring.as_ptr() as *const c_void,
            dll_path_cstring.as_bytes().len(),
            ptr::null_mut(),
        )
    };
    if write_result == 0 {
        println!("An error occurred when trying to write the DLL path in the target process.");
        return;
    }

    println!("DLL path written successfully: {:?}.", full_dll_path);

    let kernel32_handle = unsafe { GetModuleHandleA(b"kernel32.dll\0".as_ptr() as *const i8) };
    if kernel32_handle.is_null() {
        println!("An error occurred when trying to get \"LoadLibraryA\" address.");
        return;
    }

    let load_library_address = unsafe {
        GetProcAddress(
            kernel32_handle,
            b"LoadLibraryA\0".as_ptr() as *const i8,
        )
    };
    if load_library_address.is_null() {
        println!("An error occurred when trying to get \"LoadLibraryA\" address.");
        return;
    }

    println!(
        "LoadLibraryA address at 0x{:x}",
        load_library_address as usize
    );

    let thread_handle = unsafe {
        CreateRemoteThread(
            target_process,
            ptr::null_mut(),
            0,
            Some(mem::transmute(load_library_address)),
            path_address,
            0,
            ptr::null_mut(),
        )
    };
    if thread_handle.is_null() {
        println!("An error occurred when trying to create the thread in the target process.");
        return;
    }

    println!("DLL Injected!");

    unsafe {
        CloseHandle(thread_handle);
        CloseHandle(target_process);
    }
}
```
项目配置文件 Cargo.toml：
```
[package]
name = "dll_injector"
version = "0.1.0"
edition = "2021"

[dependencies]
winapi = { version = "0.3", features = ["tlhelp32", "handleapi", "libloaderapi", "memoryapi", "processthreadsapi", "winnt", "minwindef"] }
```
在项目目录下运行 cargo build --release 即可编译生成可执行文件。

注意事项：

确保已安装Rust编译器和Cargo包管理器。
在项目目录下创建 src 文件夹，并将 main.rs 文件放入其中。
将 Cargo.toml 文件放在项目根目录下。
编译后的可执行文件位于 target/release 目录下。
该Rust代码实现了与原始C++代码相同的功能，通过进程名称查找目标进程，将DLL路径写入目标进程的内存中，并在目标进程中创建远程线程来加载DLL。项目使用了 winapi 库来调用Windows API函数。

请注意，该代码仅用于教育和研究目的，在实际使用时请遵守相关法律法规。

### Round-2： 修复编译错误
说明： 问了三次才修复掉这个编译错误

**ASK:**
以上代码遇到编译错误，报错信息如下，请修正错误，并且重新给出完整代码：
--> src/main.rs:105:13
|
102 | WriteProcessMemory(
| ------------------ arguments to this function are incorrect
...
105 | dll_path_cstring.as_ptr() as *const c_void,
| ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected winapi::ctypes::c_void, found std::ffi::c_void
|


**ANS:**



### Round-3: 修复运行时错误
**ASK：**
get_process_by_name实现不正确导致程序crash，请重新实现

**ANS:**




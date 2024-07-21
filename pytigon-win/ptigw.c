#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

void get_program_path(char *pBuf, int len)
{
    int bytes = GetModuleFileName(NULL, pBuf, len), i;
    if (bytes == 0)
        pBuf[0] = 0;
    else if (bytes > 0)
    {
        for (i = bytes - 1; i > 0; i--)
        {
            if (pBuf[i] == '/' || pBuf[i] == '\\')
            {
                pBuf[i] = 0;
                break;
            }
        }
    }
}

int WINAPI WinMain(
    HINSTANCE hInstance,
    HINSTANCE hPrevInstance,
    LPSTR lpCmdLine,
    int nCmdShow)
{
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    char bufor[256], bufor2[256];

    memset(&si, 0, sizeof(si));
    si.cb = sizeof(si);

    get_program_path(bufor, 256);

    strcat(bufor, "\\python\\pythonw.exe");
    strcpy(bufor2, "\"");
    strcat(bufor2, bufor);
    strcat(bufor2, "\" -m pytigon.ptig ");
    strcat(bufor2, lpCmdLine);

    if (!CreateProcess(bufor, bufor2, NULL, NULL, 0, 0, NULL, NULL, &si, &pi))
    {
        printf("ERROR");
        getchar();
        return 0;
    }

    WaitForSingleObject(pi.hProcess, INFINITE);

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return 0;
}

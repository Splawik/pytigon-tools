#include <windows.h>
#include <stdio.h>
#include <string.h>

int get_program_path(char * pBuf, int len)
{
    int bytes = GetModuleFileName(NULL, pBuf, len), i;
    if(bytes == 0)
        pBuf[0]=0;
    else
        if(bytes>0)
        {  for(i=bytes-1; i>0; i--)
            {  if(pBuf[i]=='/' || pBuf[i]=='\\')
                {  pBuf[i]=0;
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
    char bufor[256], bufor2[256];
    get_program_path(bufor,256);
    strcat(bufor, "\\python\\pythonw.exe");
    strcpy(bufor2, "-m pytigon.ptig ");
    strcat(bufor2, lpCmdLine);
    execl(bufor, bufor, bufor2, NULL);

    return 0;
}


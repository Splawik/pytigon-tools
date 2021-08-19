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

int main(int argi, char **argv)
{
    char bufor[256];
    int i, ret;

    get_program_path(bufor,256);

    strcat(bufor, "\\python\\python.exe -m pytigon.ptig ");
    for(int i = 1; i < argi; i++)
    {  strcat(bufor, argv[i]);
       strcat(bufor, " ");
    }
    ret = system(bufor);
    return ret;
}


#pragma comment(lib,"Temperature.lib") 
extern "C" _declspec(dllimport) int _stdcall GetTempCount(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp(int Index);
extern "C" _declspec(dllimport) int _stdcall GetTemp1(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp2(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp3(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp4(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp5(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp6(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp7(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp8(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp9(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp10(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp11(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp12(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp13(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp14(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp15(void);
extern "C" _declspec(dllimport) int _stdcall GetTemp16(void);
extern "C" _declspec(dllimport) int _stdcall GetTempList(int iCardNum,int Buffer[]);
extern "C" _declspec(dllimport) int _stdcall GetTempLists(int Buffer[]);

extern "C" _declspec(dllimport) int _stdcall GetHumidityCount(void);
extern "C" _declspec(dllimport) int _stdcall GetHumidity(int Index);
extern "C" _declspec(dllimport) int _stdcall GetHumidity1(void);
extern "C" _declspec(dllimport) int _stdcall GetHumidity2(void);
extern "C" _declspec(dllimport) int _stdcall GetHumidityList(int iCardNum,int Buffer[]);
extern "C" _declspec(dllimport) int _stdcall GetHumidityLists(int Buffer[]);



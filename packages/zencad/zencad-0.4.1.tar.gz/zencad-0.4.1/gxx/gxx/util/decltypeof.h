//Макрос decltypeof имитирует поведение typeof в С/С++ коде.
//Он используется в заголовочных файлах, которые одновременно могут 
//подключаться  как из С кода, так и из С++ кода.
//Макрос должен максимально повторять поведение typeof в С++ варианте.

//#include <sys/cdefs.h>


#if __cplusplus
#	include <utility>
#	define decltypeof(a) typename std::remove_reference<decltype(a)>::type
#else
#	define decltypeof(a) __typeof__(a)
#endif
#ifndef GXX_INIT_PRIORITY_H
#define GXX_INIT_PRIORITY_H

//Макросы для изменения порядка инициализации
//Врядли совместимо.

#define GXX_PRIORITY_INITIALIZATION_SUPER 	__attribute__((init_priority(140)))
#define GXX_PRIORITY_INITIALIZATION 		__attribute__((init_priority(1000)))

#endif
#ifndef GXX_CSTRING_H
#define GXX_CSTRING_H

#include <string.h>

namespace gxx {
	class cstring {
	public:
		const char* const ptr;
		cstring(const char* ptr) : ptr(ptr) {};

		bool operator == (const char* oth) { return strcmp(ptr, oth) == 0; }
		bool operator == (const cstring oth) { return strcmp(ptr, oth.ptr) == 0; }
	
		const char* data() const { return ptr; }
		size_t size() const { return strlen(ptr); };
	};
}

#endif
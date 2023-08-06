#ifndef GXX_ALLOCATOR_H
#define GXX_ALLOCATOR_H

#include <stdlib.h>

namespace gxx {
	template<typename T>
	class allocator {
	public:
		inline T* allocate(size_t sz) {
			return (T*)malloc(sz * sizeof(T));
		};

		inline T* reallocate(void* ptr, size_t sz) {
			return (T*)realloc(ptr, sz * sizeof(T));
		};

		inline void deallocate(void* ptr) {
			free(ptr);
		};
	};
}

#endif
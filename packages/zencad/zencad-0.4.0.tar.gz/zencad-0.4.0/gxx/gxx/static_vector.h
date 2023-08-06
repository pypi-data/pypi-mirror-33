#ifndef GXX_STATIC_VECTOR_H
#define GXX_STATIC_VECTOR_H

#include <inttypes.h>

namespace gxx {
	template <typename T, size_t Cap>
	class static_vector {
		char _buf[sizeof(T) * Cap];
		T* _data;
		size_t _size;

	public:
		static_vector() : _data((T*)_buf), _size(0) {}
	};
}

#endif
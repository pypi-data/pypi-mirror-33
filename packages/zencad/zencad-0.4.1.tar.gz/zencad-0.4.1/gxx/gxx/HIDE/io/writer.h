#ifndef GXX_WRITER_H
#define GXX_WRITER_H

#include <gxx/util/numconvert.h>
#include <gxx/io/iostream.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

namespace gxx {
	class writer {
		ostream& os;

	public:
		writer(ostream& os) : os(os) {}

		virtual int write(const char* str, size_t sz) const {
			return os.write(str, sz);
		}

		virtual int putchar(char c) const {
		 	return os.putchar(c);
		}
	};

	
}

#endif
#ifndef GXX_READER_H
#define GXX_READER_H

#include <gxx/io/iostream.h>

namespace gxx {
	class reader {
	protected:
		istream& is;

	public:
		reader(istream& is) : is(is) {}

		virtual int read(char* str, size_t sz) const {
			return is.read(str, sz);
		}

		virtual int getchar() const {
		 	return is.getchar();
		}

		virtual int peek() const {
		 	return is.peek();
		}
	};
} 

#endif
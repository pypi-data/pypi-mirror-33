#ifndef GXX_IO_IOSTREAM_H
#define GXX_IO_IOSTREAM_H

#include <gxx/io/ostream.h>
#include <gxx/io/istream.h>

namespace gxx {
	namespace io {
		class iostream : public ostream, public istream {};
	}
}

#endif
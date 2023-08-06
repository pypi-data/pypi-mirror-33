#ifndef GXX_IO_STDSTREAM_H
#define GXX_IO_STDSTREAM_H

#include <gxx/io/ostream.h>
#include <string>
#include <iostream>

namespace gxx {
	namespace io {
		class ostringstream : public gxx::io::ostream {
			std::string& str;
		public:
			ostringstream(std::string& _str) : str(_str) {}
		protected:
			virtual int writeData(const char* ptr, size_t sz) {
				str.append(ptr, sz);
				return sz;
			}
		};

		/*class std_ostream_writer : public gxx::io::ostream {
			std::ostream& out;
		public:
			std_ostream_writer(std::ostream& out) : out(out) {}
		protected:
			virtual int writeData(const char* ptr, size_t sz) {
				out.write(ptr, sz);
			}
		};*/
	}
}

#endif

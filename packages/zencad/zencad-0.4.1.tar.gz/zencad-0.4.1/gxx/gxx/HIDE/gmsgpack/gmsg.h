#ifndef GXX_GMSG_H
#define GXX_GMSG_H

#include <gxx/io/strm.h>
#include <gxx/util/crc.h>

namespace gxx {

	static constexpr char GMSG_FRAMEEND = (char) 0xC0;
	static constexpr char GMSG_FRAMEESC = (char) 0xDB;
	static constexpr char GMSG_TEND = (char) 0xDC;
	static constexpr char GMSG_TESC = (char) 0xDD;

	class gmessage_writer {
		io::strmout& out;
		uint8_t crc = 0xFF;

	public:
		gmessage_writer(io::strmout& out) : out(out) {}

		void prefix() {
			out.putchar(GMSG_FRAMEEND);
			crc = 0xFF;
		}

		void postfix() {
			out.putchar(crc);			
			out.putchar(GMSG_FRAMEEND);
			crc = 0xFF;
		}

		void part(const char* data, size_t size) {
			const char* end = data + size;

			for(; data != end; data++) {
				strmcrc8(&crc, *data);
				switch (*data) {
					case (char)GMSG_FRAMEEND: 
						out.putchar(GMSG_FRAMEESC); 
						out.putchar(GMSG_TEND); 
						break;
		
					case (char)GMSG_FRAMEESC: 
						out.putchar(GMSG_FRAMEESC); 
						out.putchar(GMSG_TESC); 
						break;
		
					default:
						out.putchar(*data);
						break;
				}
			}
		}
	};
}

#endif
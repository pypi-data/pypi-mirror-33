#ifndef GXX_IO_RINGSTORAGE_H
#define GXX_IO_RINGSTORAGE_H

#include <gxx/bytering.h>
#include <gxx/io/iostorage.h>
#include <gxx/event/flag.h>

/*namespace gxx {
	namespace io {
		class ringstorage : public gxx::io::istorage {
			gxx::bytering rxring;
			gxx::event::flag* flg;

		public:
			ringstorage(gxx::buffer buf) : rxring(buf) {}
			int avail() { return rxring.avail(); }
			
			int push(char c) {
				rxring.push(c);
				flg->set();
			}

			int popn(char* dat, size_t sz) {
				int ret = rxring.popn(dat, sz);
				if (rxring.empty()) flg->clr();
				return ret;
			}

			void set_avail_flag(gxx::event::flag& flg) {
				this->flg = &flg;
			}
		};
	}
}*/

#endif
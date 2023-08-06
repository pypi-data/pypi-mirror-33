#ifndef GXX_IO_RING_STREAM_H
#define GXX_IO_RING_STREAM_H

#include <gxx/event/once_delegate.h>
#include <gxx/io/iostorage.h>
#include <gxx/bytering.h>

namespace gxx {
	namespace io {
		class ringbuffer : public gxx::io::iostorage {
			bytering ring;

			gxx::once_delegate<void> emptydlg;
			gxx::once_delegate<void> availdlg;

		public:
			ringbuffer(gxx::buffer buf) : ring(buf) {}

			int avail() override { return ring.avail(); }
			int room() override { return ring.room(); }

			int writeData(const char* str, size_t sz) override {
				ring.push(str, sz);
				availdlg();
			}

			int readData(char* str, size_t sz) override {
				ring.popn(str, sz);
				if (ring.empty()) emptydlg();
				return sz;
			}

			void dump(gxx::io::ostream& out) {
				out.print(ring.first_part_as_buffer());
				out.print(ring.last_part_as_buffer());
			}

			void dump(gxx::io::ostream&& out) { dump(out); }

			void retrans(gxx::io::ostream& out) {
				out.print(ring.first_part_as_buffer());
				out.print(ring.last_part_as_buffer());
				ring.clean();
			}

			void retrans(gxx::io::ostream&& out) { retrans(out); }

			void set_empty_callback(gxx::delegate<void> dlg) override {
				emptydlg = dlg;
			}

			void set_avail_callback(gxx::delegate<void> dlg) override {
				availdlg = dlg;
			}

		};
	}
}

#endif
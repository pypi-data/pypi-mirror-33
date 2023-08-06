#ifndef BUFWRITER_H
#define BUFWRITER_H

#include <gxx/io/ostream.h>

namespace gxx {
    namespace io {
        class bufwriter : public gxx::io::ostream {
            gxx::buffer buf;

        public:
            bufwriter(gxx::buffer buf) : buf(buf) {}

            size_t cursize = 0;

            int writeData(const char* str, size_t sz) {
                size_t last = cursize;
                cursize += sz;
                if (cursize > buf.size()) return 0;
                else memcpy(buf.data() + last, str, sz);
            }

            size_t size() {
                return cursize;
            };
        };
    }
}

#endif // BUFWRITER_H

#ifndef BUFREADER_H
#define BUFREADER_H

#include <gxx/io/iostorage.h>
#include <gxx/buffer.h>

namespace gxx {
    namespace io {
        class bufreader : public gxx::io::istorage {
            int cursor;
            gxx::buffer buf;

        public:
            bufreader(gxx::buffer buf) : buf(buf), cursor(0) {}

            int avail() {
                return buf.size() - cursor;
            }

            int readData(char* dat, size_t sz) override {
                if (cursor + sz <= buf.size())
                memcpy(dat, buf.data() + cursor, sz);
                cursor += sz;
                return sz;
            }
        };
    }
}

#endif // BUFREADER_H

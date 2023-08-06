#ifndef GXX_SERIALIZE_GBSON_H
#define GXX_SERIALIZE_GBSON_H

#include <gxx/io/iostream.h>
#include <gxx/trent/trent.h>
//#include <gxx/util/gbson.h>
#include <gxx/result.h>

namespace gxx {

	//static constexpr unsigned char gbson_integer_type = 0;
	static constexpr unsigned char gbson_numer_type = 1;
	static constexpr unsigned char gbson_bytes_type = 2;
	static constexpr unsigned char gbson_list_type = 3;
	static constexpr unsigned char gbson_dict_type = 4;

    namespace gbson {
        using namespace result_type;

        void dump(const trent& tr, gxx::io::ostream& os);
        inline void dump(const trent& tr, gxx::io::ostream&& os) { dump(tr, os); }

        result<trent> parse(gxx::io::istream& is);
        static inline result<trent> parse(gxx::io::istream&& is) { return parse(is); };
    }
}

#endif // GBSON_H

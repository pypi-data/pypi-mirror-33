#ifndef JSON_OBJECT_H
#define JSON_OBJECT_H

#include <ostream>
#include <gxx/trent/trent.h>

namespace gxx {
	namespace json {
		void print_to(const trent& tr, std::ostream& os);
		void pretty_print_to(const trent& tr, std::ostream& os, int tab = 0);

		result<trent> parse(std::istream& is);
                trent parse_numer(std::istream& is);
		result<trent> parse_string(std::istream& is);
                result<trent> parse_list(std::istream& is);
                result<trent> parse_dict(std::istream& is);
	};
}

#endif

#ifndef GXX_PARSER_TOKEN_H
#define GXX_PARSER_TOKEN_H

#include <string>

namespace gxx {

	struct token {
		char type;
		std::string text;
	};

}

#endif
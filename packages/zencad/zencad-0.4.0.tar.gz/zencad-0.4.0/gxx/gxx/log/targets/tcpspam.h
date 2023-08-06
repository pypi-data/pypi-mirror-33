#ifndef GXX_TARGET_LINUX_TCP_SOCKET_H
#define GXX_TARGET_LINUX_TCP_SOCKET_H

#include <gxx/log/target.h>
#include <gxx/inet/tcpspam_server.h>

namespace gxx { 
	namespace log {
		class tcpspam_target : public target {
			gxx::inet::tcpspam_server server;
			int port;

		public:
			tcpspam_target(int port) : port(port) {}
	
			int start() {
				return server.start(port);
			}
	
			void log(const char* str) override {
				server.print(str);
			}
		};
	}
}

#endif
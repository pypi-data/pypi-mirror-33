#ifndef GXX_INET_TCP_SERVER_H
#define GXX_INET_TCP_SERVER_H

#include <gxx/inet/tcp_socket.h>


namespace gxx {
	namespace inet {
		struct tcp_server : public inet::socket {
			tcp_server() = default;

            //tcp_server(int port);
			tcp_server(const gxx::inet::hostaddr& addr, int port, int conn = 10);
            //void listen(int port, int conn = 10);

            int init();
			int bind(const gxx::hostaddr& addr, int port);
            int listen();
            int listen(int conn);

            inet::tcp_socket accept();
		};
	}
}

#endif

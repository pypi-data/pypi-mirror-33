#include <gxx/inet/socket.h>

/*namespace gxx {

	gxx::socket socket::from_descriptor(int fd) {
		return std::move(gxx::socket().set_fd(fd));
	}

	void socket::init(socket::type type, const hostaddr& addr, uint16_t port) {
		m_addr = addr;
		m_port = port;
		m_type = type;
	}

	socket::socket() {}
	
	socket::socket(socket::type type, const hostaddr& addr, uint16_t port) {
		init(type, addr, port);
		connect();
	}


}*/
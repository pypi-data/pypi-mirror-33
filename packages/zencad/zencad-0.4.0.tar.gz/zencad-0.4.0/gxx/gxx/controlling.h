#ifndef GXX_CONTROLLING_H
#define GXX_CONTROLLING_H

#include <gxx/event/delegate.h>

namespace gxx {
	class controller;

	class controlled {
	private:
		controller* cntrl;

	public:
		void unlink_controller() {
			cntrl = nullptr;
		}

		void link_controller(controller* _cntrl) {
			cntrl = _cntrl;
		}			

		controller* controller_ptr() {
			return cntrl;
		}
	};

	class controller {
	public:
		enum class state {
			WORKED,
			STOPED,
			FINISHED,
		};

		state _state = state::STOPED;
		gxx::action finalize_handler;

		void finalize() {
			if (_state == state::WORKED) {
				_state = state::FINISHED;
				finalize_handler.emit_and_reset();
				_state = state::STOPED;
				return;
			}
		}

		void set_finalize_handler(gxx::action act) {
			finalize_handler = act;
		}

		void set_work_state() {
			_state = state::WORKED;
		}

		const char* statestr() {
			switch(_state) {
				case state::WORKED: return "WORKED";
				case state::FINISHED: return "FINISHED";
				case state::STOPED: return "STOPED";
			}
		}
	};
}

#endif 
/****************************************************************************
** Meta object code from reading C++ file 'display.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.5.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "../local/display.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'display.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.5.1. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
struct qt_meta_stringdata_servoce__disp__DisplayWidget_t {
    QByteArrayData data[3];
    char stringdata0[40];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_servoce__disp__DisplayWidget_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_servoce__disp__DisplayWidget_t qt_meta_stringdata_servoce__disp__DisplayWidget = {
    {
QT_MOC_LITERAL(0, 0, 28), // "servoce::disp::DisplayWidget"
QT_MOC_LITERAL(1, 29, 9), // "autoscale"
QT_MOC_LITERAL(2, 39, 0) // ""

    },
    "servoce::disp::DisplayWidget\0autoscale\0"
    ""
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_servoce__disp__DisplayWidget[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
       1,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   19,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void,

       0        // eod
};

void servoce::disp::DisplayWidget::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        DisplayWidget *_t = static_cast<DisplayWidget *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->autoscale(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObject servoce::disp::DisplayWidget::staticMetaObject = {
    { &QGLWidget::staticMetaObject, qt_meta_stringdata_servoce__disp__DisplayWidget.data,
      qt_meta_data_servoce__disp__DisplayWidget,  qt_static_metacall, Q_NULLPTR, Q_NULLPTR}
};


const QMetaObject *servoce::disp::DisplayWidget::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *servoce::disp::DisplayWidget::qt_metacast(const char *_clname)
{
    if (!_clname) return Q_NULLPTR;
    if (!strcmp(_clname, qt_meta_stringdata_servoce__disp__DisplayWidget.stringdata0))
        return static_cast<void*>(const_cast< DisplayWidget*>(this));
    return QGLWidget::qt_metacast(_clname);
}

int servoce::disp::DisplayWidget::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QGLWidget::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 1)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 1;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 1)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 1;
    }
    return _id;
}
struct qt_meta_stringdata_servoce__disp__MainWidget_t {
    QByteArrayData data[7];
    char stringdata0[71];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_servoce__disp__MainWidget_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_servoce__disp__MainWidget_t qt_meta_stringdata_servoce__disp__MainWidget = {
    {
QT_MOC_LITERAL(0, 0, 25), // "servoce::disp::MainWidget"
QT_MOC_LITERAL(1, 26, 5), // "about"
QT_MOC_LITERAL(2, 32, 0), // ""
QT_MOC_LITERAL(3, 33, 10), // "export_stl"
QT_MOC_LITERAL(4, 44, 10), // "screenshot"
QT_MOC_LITERAL(5, 55, 7), // "orient1"
QT_MOC_LITERAL(6, 63, 7) // "orient2"

    },
    "servoce::disp::MainWidget\0about\0\0"
    "export_stl\0screenshot\0orient1\0orient2"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_servoce__disp__MainWidget[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
       5,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   39,    2, 0x08 /* Private */,
       3,    0,   40,    2, 0x08 /* Private */,
       4,    0,   41,    2, 0x08 /* Private */,
       5,    0,   42,    2, 0x08 /* Private */,
       6,    0,   43,    2, 0x08 /* Private */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void servoce::disp::MainWidget::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        MainWidget *_t = static_cast<MainWidget *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->about(); break;
        case 1: _t->export_stl(); break;
        case 2: _t->screenshot(); break;
        case 3: _t->orient1(); break;
        case 4: _t->orient2(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

const QMetaObject servoce::disp::MainWidget::staticMetaObject = {
    { &QMainWindow::staticMetaObject, qt_meta_stringdata_servoce__disp__MainWidget.data,
      qt_meta_data_servoce__disp__MainWidget,  qt_static_metacall, Q_NULLPTR, Q_NULLPTR}
};


const QMetaObject *servoce::disp::MainWidget::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *servoce::disp::MainWidget::qt_metacast(const char *_clname)
{
    if (!_clname) return Q_NULLPTR;
    if (!strcmp(_clname, qt_meta_stringdata_servoce__disp__MainWidget.stringdata0))
        return static_cast<void*>(const_cast< MainWidget*>(this));
    return QMainWindow::qt_metacast(_clname);
}

int servoce::disp::MainWidget::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QMainWindow::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 5)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 5;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 5)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 5;
    }
    return _id;
}
QT_END_MOC_NAMESPACE

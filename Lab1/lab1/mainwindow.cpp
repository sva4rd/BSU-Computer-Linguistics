#include "mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    qApp->setStyle(QStyleFactory::create("Fusion"));
    qApp->setStyleSheet("QPushButton, QRadioButton, QHeaderView::section,"
                        "QComboBox, QCheckBox { font-weight: bold; }");
    setMinimumSize(700, 250);
    setWindowTitle("Frequency Dictionary");
    wgt = new MainWidget(this);
    setCentralWidget(wgt);
}

MainWindow::~MainWindow()
{
}

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include "mainwidget.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT
    friend class MainWidget;
public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();
private:
    MainWidget* wgt;
};
#endif // MAINWINDOW_H

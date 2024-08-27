#ifndef EDITWINDOW_H
#define EDITWINDOW_H

#include <QtWidgets>

class EditWindow : public QDialog
{
    Q_OBJECT

public:
    explicit EditWindow(QWidget* pwgt = 0);
public slots:
    void setValidator(QValidator* val);
    void setText(QString modifiedWord);

private:
    QLineEdit* input;
    QCheckBox* editTexts;
    QPushButton* okButton;
    QPushButton* cancelButton;

    QVBoxLayout* mainLay;
    QHBoxLayout* buttonLay;

private slots:
    void checkData();

signals:
    void modifiedData(QString word, bool editTexts);
};

#endif // EDITWINDOW_H

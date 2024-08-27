#ifndef ADDWINDOW_H
#define ADDWINDOW_H

#include <QtWidgets>

class AddWindow : public QDialog
{
    Q_OBJECT

public:
    explicit AddWindow(QWidget* pwgt = 0);
    void clearData();
public slots:
    void setValidator(QValidator* val);

private:
    QString currentPath;

    QGridLayout* mainLay;
    QHBoxLayout* answerButtonLay;
    QVBoxLayout* radioLay;
    QVBoxLayout* textLay;
    QVBoxLayout* wordLay;

    QGroupBox* listBox;
    QGroupBox* wordBox;
    QGroupBox* textBox;

    QRadioButton* wordButton;
    QRadioButton* textButton;

    QLineEdit* wordLine;
    QTextEdit* textLine;
    QPushButton* textFileButton;
    QPushButton* okButton;
    QPushButton* cancelButton;

    QSpacerItem* answerSpacer;

    void showWordBox();
    void showTextBox();

private slots:
    void checkData();
    void selectTextFile();

signals:
    void newWord(QString word);
    void newText(QString text);
};

#endif // ADDWINDOW_H

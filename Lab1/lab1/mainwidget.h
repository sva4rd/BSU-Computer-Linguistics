#ifndef MAINWIDGET_H
#define MAINWIDGET_H

#include <QtWidgets>
#include "mainwindow.h"
#include "addwindow.h"
#include "editwindow.h"

class MainWidget : public QWidget
{
    Q_OBJECT
    friend class MainWindow;
public:
    explicit MainWidget(QWidget *parent = nullptr);
    ~MainWidget();

private:
    void up();
    QLabel *wordsLbl;
    QVector<QMap<QString, int>> dictionaries;
    const QString saveFileName = "Data/dictionaries.dat";
    const QString textAmountFileNAme = "Data/textNum.dat";
    const QString textsDir = "Data/texts/";
    long long textNum;
    const int langCount = 3;
    QVector<QValidator*> wordVal;
    QVector<QRegularExpression> regExps;
    QTableWidgetItem* lastFocused;

    AddWindow* addWgt;
    EditWindow* editWgt;

    QComboBox* chooseLanguage;
    QTableWidget* dictionaryTable;
    QPushButton* addButton;
    QPushButton* editButton;
    QPushButton* delButton;

    QLineEdit* searchLine;
    QPushButton* searchButton;
    QTableWidget* resultTable;

    QGridLayout* mainLay;
    QHBoxLayout* buttonsLay;
    QVBoxLayout* leftLay;
    QHBoxLayout* searchLay;
    QVBoxLayout* rightLay;

    void createValidators();
    void setLanguageComboBox();
    void setDictionaryTable();
    void setResultTable();
    void changeTexts(QString oldWord, QString word);

    void resizeEvent(QResizeEvent* event) override;

    void saveData();
    void loadData();
    void createUnloadedDictionaries();
    void updateTable();

    QString wordProccessing(QString word);

private slots:
    void addProccess();
    void editProccess();
    void deleteProccess();
    void changeDictionary();
    void searchWords();
    void selectSearchResult();
    void changeFocus();

    void getModifiedWord(QString word, bool editTexts);
    void getNewWord(QString word);
    void getNewText(QString text);

signals:
    void sendValidator(QValidator* val);
    void sendCurrentWord(QString word);
};

#endif // MAINWIDGET_H

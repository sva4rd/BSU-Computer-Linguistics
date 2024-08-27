#include "addwindow.h"

AddWindow::AddWindow(QWidget* pwgt):QDialog(pwgt)
{
    currentPath = QDir::currentPath();

    setWindowTitle("Add Item");
    listBox = new QGroupBox;
    textBox = new QGroupBox;
    wordBox = new QGroupBox;

    radioLay = new QVBoxLayout;
    wordButton = new QRadioButton(this);
    wordButton->setText("Word");
    textButton = new QRadioButton(this);
    textButton->setText("Text");
    radioLay->addWidget(wordButton);
    radioLay->addWidget(textButton);
    radioLay->addStretch(1);
    listBox->setLayout(radioLay);

    wordLay = new QVBoxLayout;
    wordLine = new QLineEdit(this);
    wordLine->setPlaceholderText("Enter a new word");
    wordLay->addWidget(wordLine);
    wordBox->setLayout(wordLay);

    textLay = new QVBoxLayout;
    textLine = new QTextEdit(this);
    textLine->setPlaceholderText("Enter text to add");
    textFileButton = new QPushButton(this);
    textFileButton->setText("Choose text file");
    textLay->addWidget(textLine);
    textLay->addWidget(textFileButton);
    textBox->setLayout(textLay);

    answerButtonLay = new QHBoxLayout;
    okButton = new QPushButton(this);
    okButton->setText("Ok");
    cancelButton = new QPushButton(this);
    cancelButton->setText("Cancel");
    answerButtonLay->addStretch(1);
    answerButtonLay->addWidget(okButton);
    answerButtonLay->addWidget(cancelButton);
    answerSpacer = new QSpacerItem(6, 1);

    mainLay = new QGridLayout(this);
    mainLay->addWidget(listBox, 0, 0);
    mainLay->addWidget(wordBox, 0, 1);
    mainLay->addWidget(textBox, 0, 2);
    mainLay->addLayout(answerButtonLay, 1, 0, 1, 3);

    connect(wordButton, &QRadioButton::clicked, this, &AddWindow::showWordBox);
    connect(textButton, &QRadioButton::clicked, this, &AddWindow::showTextBox);

    clearData();
    connect(okButton, &QPushButton::clicked, this, &AddWindow::checkData);
    connect(cancelButton, SIGNAL(clicked()), SLOT(reject()));

    connect(textFileButton, &QPushButton::clicked, this, &AddWindow::selectTextFile);
}

void AddWindow::setValidator(QValidator *val)
{
    wordLine->setValidator(val);
}

void AddWindow::checkData()
{
    if (wordButton->isChecked() && !wordLine->text().isEmpty() && wordLine->text().last(1) != '-'){
        emit(AddWindow::newWord(wordLine->text()));
        accept();
        return;
    }
    if (textButton->isChecked() && !textLine->toPlainText().isEmpty() /*&& textLine->toPlainText()*/){
        emit(AddWindow::newText(textLine->toPlainText()));
        accept();
        return;
    }
    QMessageBox::warning(this, "Error", "Misspelling");
}

void AddWindow::selectTextFile()
{
    //QTextCodec::setCodecForLocale(QTextCodec::codecForName("UTF-8"));
    QString fileName = QFileDialog::getOpenFileName(this, "Open File", currentPath, "Text(*txt)");
    if(fileName.isEmpty())
        return;
    QFileInfo filePath;
    filePath.setFile(fileName);
    currentPath = filePath.path();

    QFile in(fileName);
    if(in.open( QIODevice::ReadOnly)) {
        QTextStream stream(&in);
        QString line = stream.readAll();
        if(!line.isEmpty()){
            emit(newText(line));
            in.close();
            accept();
            return;
        }
        QMessageBox::warning(this, "Error", "Text file is empty");
        in.close();

    }
}

void AddWindow::clearData()
{
    wordLine->clear();
    textLine->clear();
    wordButton->setChecked(true);
    emit(wordButton->clicked());
}


void AddWindow::showWordBox()
{
    answerButtonLay->addSpacerItem(answerSpacer);
    setMinimumSize(283, 140);
    setMaximumSize(350, 140);
    textBox->setHidden(true);
    wordBox->show();
    resize(283, 140);
}

void AddWindow::showTextBox()
{
    answerButtonLay->removeItem(answerSpacer);
    setMinimumSize(350, 200);
    setMaximumSize(700, 600);
    wordBox->setHidden(true);
    textBox->show();
    resize(400, 300);
}

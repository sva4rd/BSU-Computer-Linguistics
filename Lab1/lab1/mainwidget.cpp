#include "mainwidget.h"

MainWidget::MainWidget(QWidget *parent)
    : QWidget{parent}
{
    createValidators();
    addWgt = new AddWindow(this);
    editWgt = new EditWindow(this);
    setLanguageComboBox();
    setDictionaryTable();

    addButton = new QPushButton(this);
    addButton->setText("Add");
    editButton = new QPushButton(this);
    editButton->setText("Edit");
    delButton = new QPushButton(this);
    delButton->setText("Delete");

    searchLine = new QLineEdit(this);
    searchButton = new QPushButton(this);
    searchButton->setText("Search");
    setResultTable();
    wordsLbl = new QLabel(this);

    buttonsLay = new QHBoxLayout();
    buttonsLay->addWidget(addButton);
    buttonsLay->addWidget(editButton);
    buttonsLay->addWidget(delButton);

    leftLay = new QVBoxLayout();
    leftLay->addWidget(chooseLanguage);
    leftLay->addWidget(dictionaryTable);
    leftLay->addLayout(buttonsLay);

    searchLay = new QHBoxLayout();
    searchLay->addWidget(searchLine);
    searchLay->addWidget(searchButton);

    rightLay = new QVBoxLayout();
    rightLay->addSpacing(30);
    rightLay->addLayout(searchLay);
    rightLay->addWidget(resultTable);
    rightLay->addWidget(wordsLbl);////
    rightLay->addSpacing(30);

    mainLay = new QGridLayout(this);
    mainLay->addLayout(leftLay, 0, 0, 8, 4);
    mainLay->addLayout(rightLay, 0, 4, 8, 2);

    connect(addButton, &QPushButton::clicked, this, &MainWidget::addProccess);
    connect(editButton, &QPushButton::clicked, this, &MainWidget::editProccess);
    connect(delButton, &QPushButton::clicked, this, &MainWidget::deleteProccess);
    connect(chooseLanguage, &QComboBox::currentTextChanged, this, &MainWidget::changeDictionary);
    connect(searchButton, &QPushButton::clicked, this, &MainWidget::searchWords);
    connect(resultTable, &QTableWidget::cellClicked, this, &MainWidget::selectSearchResult);
    connect(dictionaryTable, &QTableWidget::itemClicked, this, &MainWidget::changeFocus);

    connect(this, &MainWidget::sendValidator, addWgt, &AddWindow::setValidator);
    connect(this, &MainWidget::sendValidator, editWgt, &EditWindow::setValidator);
    connect(this, &MainWidget::sendCurrentWord, editWgt, &EditWindow::setText);
    connect(editWgt, &EditWindow::modifiedData, this, &MainWidget::getModifiedWord);
    connect(addWgt, &AddWindow::newWord, this, &MainWidget::getNewWord);
    connect(addWgt, &AddWindow::newText, this, &MainWidget::getNewText);

    loadData();
    //chooseLanguage->setCurrentIndex(1);
    changeDictionary();
//    dictionaryTable->sortByColumn(1, Qt::SortOrder::DescendingOrder);
//    QTableWidgetSelectionRange range(0, 1, dictionaryTable->rowCount()-1, 1);
//    dictionaryTable->setRangeSelected(range, true);
//    QItemSelectionModel *select = dictionaryTable->selectionModel();

//    if (select->hasSelection()) // если есть выбранные ячейки
//    {
//        QString str;
//        QModelIndexList indexes = select->selectedIndexes();
//        //std::sort(indexes.begin(), indexes.end());

//        for (int i = 0; i < indexes.count(); ++i)
//        {
//            QModelIndex current = indexes[i];
//            QString text = current.data().toString();
//            str.append(text);
//            if (i < indexes.count() - 1) {
//                str.append("\n");
//            }
//        }
//        QApplication::clipboard()->setText(str);
//    }
}

MainWidget::~MainWidget()
{
    for (auto i = 0; i < wordVal.size(); ++i)
        delete wordVal[i];
    saveData();
}

void MainWidget::up()
{
    int cur = chooseLanguage->currentIndex();
    int sum = 0;
    QList<int> values = dictionaries[cur].values();
    sum = std::accumulate(values.begin(), values.end(), 0);
    if (chooseLanguage->currentIndex() == 0)
        wordsLbl->setText(QString::number(sum) + " words");
    else if (chooseLanguage->currentIndex() == 1)
        wordsLbl->setText(QString::number(sum) + " words");
    else if (chooseLanguage->currentIndex() == 2)
        wordsLbl->setText(QString::number(sum) + " words");
}

void MainWidget::createValidators()
{
    regExps.append(QRegularExpression("([А-Яа-я]+-[А-Яа-я]+)|([А-Яа-я]+)"));
    regExps.append(QRegularExpression("([A-Za-z]+-[A-Za-z]+)|([A-Za-z]+)"));
    for (auto it = regExps.begin(); it < regExps.end(); ++it)
        wordVal.append(new QRegularExpressionValidator(*it));
}

void MainWidget::setLanguageComboBox()
{
    chooseLanguage = new QComboBox(this);
    chooseLanguage->addItem("Russian Dictionary", QVariant(0));
    chooseLanguage->addItem("English Dictionary", QVariant(1));
    chooseLanguage->addItem("Spanish Dictionary", QVariant(2));
}

void MainWidget::setDictionaryTable()
{
    dictionaryTable = new QTableWidget(this);
    dictionaryTable->setSortingEnabled(true);
    dictionaryTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    dictionaryTable->setColumnCount(2);
    QStringList headers;
    headers << "Words" << "Frequencies";
    dictionaryTable->setHorizontalHeaderLabels(headers);
    dictionaryTable->horizontalHeader()->setSectionResizeMode(1, QHeaderView::Stretch);
    dictionaryTable->horizontalHeader()->setStretchLastSection(false);
    dictionaryTable->verticalHeader()->setSectionResizeMode(QHeaderView::Fixed);
}

void MainWidget::setResultTable()
{
    resultTable = new QTableWidget(this);
    resultTable->setColumnCount(1);
    resultTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    resultTable->setEditTriggers(QAbstractItemView::NoEditTriggers);
    QStringList headers;
    headers << "Sort";
    resultTable->setHorizontalHeaderLabels(headers);
    resultTable->setSortingEnabled(true);
}

void MainWidget::changeTexts(QString oldWord, QString word)
{
    QDir directory(textsDir);
    QStringList txtFiles = directory.entryList(QStringList() << "*.txt", QDir::Files);

    foreach(QString filename, txtFiles) {
        QFile file(directory.absoluteFilePath(filename));
        if (file.open(QIODevice::ReadWrite | QIODevice::Text)) {
            QString text = file.readAll();
            text.replace(oldWord, word);
            file.resize(0);
            QTextStream out(&file);
            out << text;
            file.close();
        }
    }
}

void MainWidget::resizeEvent(QResizeEvent *event)
{
    Q_UNUSED(event);
    dictionaryTable->horizontalHeader()->resizeSection(0, dictionaryTable->width()*0.7);
    dictionaryTable->horizontalHeader()->resizeSection(1, dictionaryTable->width()*0.3);
}

void MainWidget::addProccess()
{
    addWgt->clearData();
    addWgt->exec();
    up();
}

void MainWidget::editProccess()
{
    QList<QTableWidgetItem*> selectedItems = dictionaryTable->selectedItems();
    if (selectedItems.size() != 1){
        QMessageBox::warning(this, "Error", "Select only one item");
        return;
    }
    emit(sendCurrentWord(dictionaryTable->item(dictionaryTable->currentRow(), 0)->text()));
    editWgt->exec();
    up();
}

void MainWidget::deleteProccess()
{
    up();
    if (dictionaryTable->currentItem() == nullptr){
        QMessageBox::warning(this, "Error", "No selected item");
        return;
    }
    int result = QMessageBox::question(this, "Delete Item", "Are you sure you want to "
                                                            "delete the selected items?");
    if (result == QMessageBox::No)
        return;

    searchLine->clear();
    resultTable->clearContents();
    resultTable->setRowCount(0);
    QList<QTableWidgetItem*> selectedItems = dictionaryTable->selectedItems();
    QList<int> rows;
    for (QTableWidgetItem* item : selectedItems) {
        int row = item->row();
        if (!rows.contains(row)){
            rows.append(row);
            dictionaries[chooseLanguage->currentIndex()].remove(item->text());
        }
    }

    std::sort(rows.begin(), rows.end(), std::greater<int>());
    for (int row : rows)
        dictionaryTable->removeRow(row);

    dictionaryTable->setCurrentItem(nullptr);
}

void MainWidget::changeDictionary()
{

    updateTable();
    if (chooseLanguage->currentIndex() == 0){
        searchLine->setValidator(wordVal[0]);
        emit(sendValidator(wordVal[0]));
    }
    else{
        searchLine->setValidator(wordVal[1]);
        emit sendValidator(wordVal[1]);

    }
    up();
}

void MainWidget::searchWords()
{
    resultTable->clearContents();
    resultTable->setRowCount(0);
    if (searchLine->text().isEmpty())
        return;

    int dictNum = chooseLanguage->currentIndex();
    QString word = searchLine->text().toLower();
    int row = 0;
    for (auto it = dictionaries[dictNum].begin(); it != dictionaries[dictNum].end(); ++it) {
        if (it.key().toLower().startsWith(word)){
            QTableWidgetItem* item = new QTableWidgetItem(it.key());
            resultTable->insertRow(row);
            resultTable->setItem(row++, 0, item);
        }
    }
}

void MainWidget::selectSearchResult()
{
    QString word = resultTable->currentItem()->text();
    for (int i = 0; i < dictionaryTable->rowCount(); ++i) {
        QTableWidgetItem* item = dictionaryTable->item(i, 0);
        if (item && item->text() == word) {
            dictionaryTable->setCurrentItem(item);
            break;
        }
    }
}

void MainWidget::changeFocus()
{
    if (lastFocused != dictionaryTable->currentItem()){
        lastFocused = dictionaryTable->currentItem();
        return;
    }
    lastFocused = nullptr;
    dictionaryTable->setCurrentItem(nullptr);
}

void MainWidget::getModifiedWord(QString word, bool editTexts)
{
    int current = chooseLanguage->currentIndex();
    auto wordIter = dictionaries[current].find(word);
    QString oldWord;

    if (wordIter != dictionaries[current].end()){
        wordIter.value() += dictionaryTable->item(dictionaryTable->currentRow(), 1)->text().toInt();
        oldWord = dictionaryTable->item(dictionaryTable->currentRow(), 0)->text();
        dictionaries[current].remove(oldWord);
        dictionaryTable->removeRow(dictionaryTable->currentRow());
        QList<QTableWidgetItem*>item = dictionaryTable->findItems(wordIter.key(), Qt::MatchFixedString);
        dictionaryTable->setCurrentItem(item[0]);
        item[0] = new QTableWidgetItem;
        item[0]->setData(Qt::EditRole, wordIter.value());
        dictionaryTable->setItem(dictionaryTable->currentRow(), 1, item[0]);
    }
    else {
        auto oldTableWord = dictionaryTable->item(dictionaryTable->currentRow(), 0);
        oldWord = oldTableWord->text();
        auto oldDictWord = dictionaries[current].find(oldWord);
        int value = oldDictWord.value();
        dictionaries[current].remove(oldWord);
        dictionaries[current].insert(word, value);
        oldTableWord->setText(word);
    }

    if (editTexts)
        changeTexts(oldWord, word);
}

void MainWidget::getNewWord(QString word)
{
    int current = chooseLanguage->currentIndex();
    if(dictionaries[current].find(word)!=dictionaries[current].end()){
        QMessageBox::warning(this, "Error", "This isn't a new word!");
        return;

    }
    dictionaries[current].insert(word, 0);
    dictionaryTable->insertRow(dictionaryTable->rowCount());
    QTableWidgetItem* keyItem = new QTableWidgetItem(word);
    QTableWidgetItem* valueItem = new QTableWidgetItem;
    valueItem->setData(Qt::EditRole, 0);
    dictionaryTable->setItem(dictionaryTable->rowCount()-1, 0, keyItem);
    dictionaryTable->setItem(dictionaryTable->rowCount()-1, 1, valueItem);
}

void MainWidget::getNewText(QString text)
{
    int current = chooseLanguage->currentIndex();
    QRegularExpression rx;
    if (chooseLanguage->currentIndex() == 0)
        rx = QRegularExpression("([А-Яа-я]+-[А-Яа-я]+)|([А-Яа-я]+)");
    else
        rx = QRegularExpression("([A-Za-z]+-[A-Za-z]+)|([A-Za-z]+)");
    QRegularExpressionMatchIterator i = rx.globalMatch(text);
    QString word;
    QRegularExpressionMatch match;
    while (i.hasNext()) {
        match = i.next();
        if (match.captured(1).isEmpty())
            word = match.captured(2);
        else
            word = match.captured(1);
        word = wordProccessing(word);

        if (dictionaries[current].contains(word))
            dictionaries[current][word]++;
        else
            dictionaries[current].insert(word, 1);
    }
    updateTable();

    QFile file(textsDir + QString::number(textNum + 1) + ".txt");
    if (file.open(QIODevice::WriteOnly | QIODevice::Text)) {
        textNum++;
        QTextStream out(&file);
        out << text;
        file.close();
    }
}

void MainWidget::saveData()
{
//    QFile dictFile(saveFileName);
//    if (!dictFile.open(QIODevice::WriteOnly)){
//        QMessageBox::warning(0, "Error", "Unable to save data");
//        dictFile.close();
//        return;
//    }
//    QDataStream out(&dictFile);
//    out << dictionaries;
//    dictFile.close();

    QFile dictFile("Data/Russian_dictionary.dat");
    QFile dictFile2("Data/English_dictionary.dat");
    QFile dictFile3("Data/Spanish_dictionary.dat");
    if (!dictFile.open(QIODevice::WriteOnly)){
        QMessageBox::warning(0, "Error", "Unable to save data");
        dictFile.close();
        return;
    }
    dictFile2.open(QIODevice::WriteOnly);
            dictFile3.open(QIODevice::WriteOnly);
    QDataStream out(&dictFile);
    QDataStream out2(&dictFile2);
    QDataStream out3(&dictFile3);
    out << dictionaries[0];
    out2 << dictionaries[1];
    out3 << dictionaries[2];
    dictFile.close();
    dictFile2.close();
    dictFile3.close();


    QFile textAmoutFile(textAmountFileNAme);
    if (!textAmoutFile.open(QIODevice::WriteOnly)){
        //QMessageBox::warning(0, "Error", "Unable to save data");
        textAmoutFile.close();
        return;
    }
    QDataStream outTextAmount(&textAmoutFile);
    outTextAmount << textNum;
    textAmoutFile.close();
}

void MainWidget::loadData()
{
    QDir directory(textsDir);
    if (!directory.exists())
        directory.mkpath(".");

    //QFile file(saveFileName);
    dictionaries.append(QMap<QString, int>());
    dictionaries.append(QMap<QString, int>());
    dictionaries.append(QMap<QString, int>());
    QFile dictFile("Data/Russian_dictionary.dat");
    QFile dictFile2("Data/English_dictionary.dat");
    QFile dictFile3("Data/Spanish_dictionary.dat");
    dictFile.open(QIODevice::ReadOnly);
    dictFile2.open(QIODevice::ReadOnly);
    dictFile3.open(QIODevice::ReadOnly);
    //if (!file.open(QIODevice::ReadOnly)){
//        QMessageBox::warning(0, "Error", "Unable to load data");
//        QDir dir(QDir::currentPath() + "/Data");
//        if (!dir.exists())
//            dir.mkpath(".");
//        createUnloadedDictionaries();
    //}
    //else {
//        QDataStream in(&file);
//        in >> dictionaries;
//        file.close();
        QDataStream out(&dictFile);
        QDataStream out2(&dictFile2);
        QDataStream out3(&dictFile3);
        out >> dictionaries[0];
        out2 >> dictionaries[1];
        out3 >> dictionaries[2];
        dictFile.close();
        dictFile2.close();
        dictFile3.close();
        createUnloadedDictionaries();
    //}

    textNum = 0;
    bool fileNotExist = false;
    QFile textAmountFile(textAmountFileNAme);
    if (textAmountFile.size() == 0)
        fileNotExist = true;
    if (!textAmountFile.open(QIODevice::ReadOnly) || fileNotExist)
        return;
    QDataStream inTextAmount(&textAmountFile);
    inTextAmount >> textNum;
    textAmountFile.close();
}

void MainWidget::createUnloadedDictionaries()
{
    while(dictionaries.size() < langCount)
        dictionaries.append(QMap<QString, int>());
}

void MainWidget::updateTable()
{
    dictionaryTable->clearContents();
    dictionaryTable->setRowCount(0);
    int dictNum = chooseLanguage->currentIndex();
    int row = 0;
    if (dictionaries.isEmpty() || dictionaries[dictNum].isEmpty()){
        return;
    }
    dictionaryTable->setSortingEnabled(false);
    dictionaryTable->setRowCount(dictionaries[dictNum].size());
    for (auto it = dictionaries[dictNum].begin(); it != dictionaries[dictNum].end(); ++it, ++row) {
        QTableWidgetItem* keyItem = new QTableWidgetItem(it.key());
        QTableWidgetItem* valueItem = new QTableWidgetItem;
        valueItem->setData(Qt::EditRole, it.value());
        dictionaryTable->setItem(row, 0, keyItem);
        dictionaryTable->setItem(row, 1, valueItem);
    }
    dictionaryTable->setSortingEnabled(true);
}

QString MainWidget::wordProccessing(QString word)
{
    QChar firstLetter = word[0];
    QChar secondLetter;
    int index = word.indexOf('-');
    if (index != -1 && index + 1 < word.length())
        secondLetter = word.at(index + 1);
    word = word.toLower();
    word[0] = firstLetter;
    if (index != -1 && index + 1 < word.length())
        word[index + 1] = secondLetter;
    return word;
}

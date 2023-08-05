import torchext

dataset = torchext.data.CsvDataset("/data/private/qa/data/qgen/20180531.squad.en.sel1/train.csv")
dataset = dataset.repeat()
for i, sample in enumerate(dataset):
    if i % 100000 == 0:
        print(i)

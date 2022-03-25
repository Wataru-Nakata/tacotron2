from argparse import ArgumentParser
from pathlib import Path
import soundfile as sf
import pandas as pd
from sklearn.model_selection import train_test_split

def duration_from_label(label:str):
    duration_ns = int(label.split(" ")[1]) - int(label.split(" ")[0])
    return duration_ns

def remove_silence(
        corpus_dir:str, 
        output_dir:str,
        label_root_dir='external_resources/jsut-lab/',
    ):
    corpus_root_dir = Path(corpus_dir)
    label_root_dir = Path(label_root_dir)
    output_dir = Path(output_dir)

    transcriptions_dict = {}
    transcriptions = []
    wav_files = []
    for corpus_subset in corpus_root_dir.iterdir():
        if not (corpus_root_dir/corpus_subset).is_dir():
            continue
        with open(corpus_root_dir/corpus_subset/'transcript_utf8.txt') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip().split(':')
            transcriptions_dict[line[0]] = line[1]
        for wav_file in (corpus_root_dir/corpus_subset).glob("**/*.wav"):
            label_file = label_root_dir.glob("**/{}.lab".format(wav_file.stem))
            label_file = list(label_file)
            assert  len(label_file) == 1
            with open(label_file[0]) as f:
                labels = f.readlines()
            start_silence = duration_from_label(labels[0])
            end_silence = duration_from_label(labels[-1])
            wav,sr = sf.read(wav_file)
            transcriptions.append(transcriptions_dict[wav_file.stem])
            output_wav = wav[int(start_silence*sr/1e9*100):int(-end_silence*sr/1e9*100)]
            print(wav.shape,output_wav.shape)
            sf.write(output_dir/wav_file.name,output_wav,sr)
            wav_files.append(str(output_dir/wav_file.name))
    return wav_files, transcriptions


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--corpusDir",required=True, help="path to jsut corpus")
    parser.add_argument("--outputDir",required=True, help="path to output wavs")
    args = parser.parse_args()
    wav_files, transcriptions = remove_silence(args.corpusDir, args.outputDir)
    df = pd.DataFrame()
    df['wav_files'] = wav_files
    df['transcriptions'] = transcriptions
    df.to_csv(Path(args.outputDir)/"filelist.txt",sep='|',header=None, index=None)
    train_df, test_df = train_test_split(df,test_size=100,random_state=42)
    train_df, val_df = train_test_split(df,test_size=100,random_state=22)
    train_df.to_csv(Path('filelists/')/"jsut_train.txt",sep='|',header=None, index=None)
    val_df.to_csv(Path('filelists/')/"jsut_val.txt",sep='|',header=None, index=None)
    test_df.to_csv(Path('filelists/')/"jsut_test.txt",sep='|',header=None, index=None)


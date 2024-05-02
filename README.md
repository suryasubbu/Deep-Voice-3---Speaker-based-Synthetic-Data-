# Deep Voice 3 - Speaker Based Synthetic Data Generation


Project is based on https://github.com/Kyubyong/deepvoice3 
it is updated to new tensorflow version 
Abstract
This work presents Deep Voice 3, a novel Text-to-Speech (TTS) system leveraging a fully-convolutional, attention-based neural network architecture. Unlike its predecessors, Deep Voice 3 offers a blend of natural-sounding voice synthesis with remarkable efficiency in training and synthesis speed. Our approach addresses the challenge of scalability in TTS, enabling the model to learn from a dataset comprising over 800 hours of speech from more than 2,000 speakers. Experimental results demonstrate the system's superiority in voice naturalness and computational performance compared to existing technologies.
Introduction
The evolution of Text-to-Speech (TTS) technology over the years has been remarkable, transitioning from synthetic, robotic outputs to remarkably natural-sounding voices. This progress has not only enhanced user experience across various applications but also paved the way for more sophisticated conversational AI technologies. Among the breakthroughs in this domain, Deep Voice 3 represents a significant milestone, heralding a new era of voice synthesis with its advanced neural network architecture.
Deep Voice 3 Overview

Deep Voice 3 is an attention-based, fully convolutional neural network designed specifically for TTS tasks. Unlike its predecessors, which relied on complex, multi-stage processing pipelines, Deep Voice 3 simplifies voice synthesis into a more streamlined process. The system is trained on an extensive dataset, comprising over 800 hours of audio from more than 2,000 speakers, enabling it to produce a wide array of voice outputs with unprecedented naturalness.
Data Pipeline


The first step in the data pipeline involves gathering audio files, typically in .wav format, each approximately one minute in length. These files are accompanied by textual metadata, which plays a crucial role in subsequent processing stages.
Speech Enhancement
The speech enhancement phase is crucial for ensuring the quality of the audio input. This stage consists of two key processes:
•	Denoiser: Utilizing a UNet model, this process separates speech from background noise, effectively purifying the audio data.
•	Enhancer: Employing a conditional flow matching model, the enhancer further refines the speech quality, ensuring clarity and naturalness.
Transcribing
Following enhancement, the audio files undergo transcription. This process leverages the Whisper architecture, a Transformer-based model adept at converting speech to text with high accuracy. This stage is pivotal in creating accurate textual representations of the audio data.
Model Training
With the data prepared and enhanced, the Deep Voice 3 architecture—comprising an encoder, a decoder, and a converter—is trained. Each component plays a vital role:
•	Encoder: Converts characters or phonemes into vector representations, extracting and processing textual information.
•	Decoder: Predicts future audio frames from past frames, generating mel-spectrograms in an autoregressive manner.
•	Converter: Transforms the output of the decoder into parameters suitable for various vocoders, facilitating waveform synthesis.

Results
Deep Voice 3 sets a new benchmark in the TTS domain, matching and surpassing existing neural speech synthesis systems in naturalness while achieving significantly faster training times. It effectively addresses common TTS challenges, such as mispronunciations, word repetitions, and skips, offering a solution that is both efficient and high quality.
Conclusion
Deep Voice 3 marks a significant advancement in TTS technology, streamlining the voice synthesis pipeline and offering a level of naturalness previously unattainable. Its fully convolutional architecture, combined with an effective data pipeline, positions Deep Voice 3 as a foundational technology for the next generation of conversational AI applications.


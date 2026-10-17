# Practitioner discussions about models that won't stop

Collected from the Hugging Face forum (Discourse search API, 8 queries) and Hacker News (Algolia
API, 13 queries), 2026-10-17. Only threads relevant to stopping are listed. They show the
same few symptoms appearing again and again, which is useful as a "real-world relevance"
paragraph for the paper.

## Recurring symptoms

1. **Fine-tuning silently removes the stop decision.** Using `pad_token = eos_token` with a
   collator that masks pad positions also masks the only EOS label, so the model never sees a
   stop target and learns to run on.
   - [GPT2 finetuned with eos token will never yield eos token during generation](https://discuss.huggingface.co/t/gpt2-finetuned-with-eos-token-will-never-yield-eos-token-during-generation/15437) (2022)
   - [Why does the falcon QLoRA tutorial code use eos_token as pad_token?](https://discuss.huggingface.co/t/why-does-the-falcon-qlora-tutorial-code-use-eos-token-as-pad-token/45954) (2023)
   - [Model fine-tuning not respecting <|endoftext|> stop tokens during training](https://discuss.huggingface.co/t/model-fine-tuning-not-respecting-endoftext-stop-tokens-during-training/169880) (2025)
   - [HF Trainer: T5 doesn't generate eos token at proper point](https://discuss.huggingface.co/t/hf-trainer-hf-trainer-cause-a-problem-while-fine-tuning-t5-t5-doesnt-generate-eos-token-at-proper-point/15411) (2022)
   - [Codellama will not stop generating at EOS](https://discuss.huggingface.co/t/codellama-will-not-stop-generating-at-eos/66513) (2023)
2. **What the model does instead of stopping: it simulates the next turn.**
   - [LLaMA-3 fine-tuning: model generates correct answer but then adds unrelated questions](https://discuss.huggingface.co/t/issue-with-llama-3-fine-tuning-model-generates-correct-answer-but-then-adds-unrelated-questions/149141) (2025)
   - [How to prevent LLM from generating multiple rounds of conversation?](https://discuss.huggingface.co/t/how-to-prevent-llm-from-generating-multiple-rounds-of-conversation/41847) (2023)
   - [`<|im_end|>\n<|im_start|>assistant` generated despite predict model used](https://discuss.huggingface.co/t/im-end-n-im-start-assistant-generated-despite-predict-model-used/171444) (2025)
   - [P-tuned Phi-2 produces open ended, repeating, responses](https://discuss.huggingface.co/t/p-tuned-phi-2-produces-open-ended-repeating-responses/84210) (2024)
   - [Reducing unwanted generation in Gemma 3](https://discuss.huggingface.co/t/reducing-unwanted-generation-in-gemma-3/148856) (2025)
3. **People ask how the stop decision is made at all**, and get folk answers.
   - [How does GPT decide to stop generating sentences without EOS token?](https://discuss.huggingface.co/t/how-does-gpt-decide-to-stop-generating-sentences-without-eos-token/41623) (2023)
   - [How can I stop text generation naturally … without using a hard max token limit?](https://discuss.huggingface.co/t/how-can-i-stop-text-generation-naturally-in-an-llm-running-locally-with-hugging-face-without-using-a-hard-max-token-limit/116300) (2024)
   - [How to make T5 model know when to stop generating during inference?](https://discuss.huggingface.co/t/how-to-make-t5-model-know-when-to-stop-generating-during-inference/168788) (2025)
4. **Sampling settings change how long models talk.**
   - [Model produces chaotic / repetitive output when top_k is higher](https://discuss.huggingface.co/t/model-produces-chaotic-repetitive-output-when-top-k-is-higher-how-to-fix-this/170966) (2025)
   - [Repetitive answers from fine-tuned LLM](https://discuss.huggingface.co/t/repetitive-answers-from-fine-tuned-llm/110024) (2026)

## Hacker News

- [Efficient streaming language models with attention sinks](https://news.ycombinator.com/item?id=37740932) (421 points, 2023)
- [How attention sinks keep language models stable](https://news.ycombinator.com/item?id=44834918) (219 points, 2025)

Nothing on HN discusses removing EOS as a research intervention. Reddit, LessWrong and the
Alignment Forum were blocked by this environment's network policy and were not scanned from the
container; the web-search literature agents covered them where they could.

# Project Proposal

**Team:** Jayminn Anand, Yann Bellac, Srikar Mannam

## Experimental question

Do brainwave patterns at the back of the brain look different during REM sleep compared to NREM sleep, in a way that matches the EEG signature of dreaming described by Siclari et al. (2017)?

## Background

For some time scientists thought that dreaming only happened during REM sleep stages. But when researchers wake up people during NREM sleep and ask if they were dreaming around 60–70% of the time they said yes. There have even been cases where when people are waken up from REM sleep and asked if they were dreaming, they said no. So the sleep stage alone doesn't really tell us if someone is dreaming at times. This topic raises a big question in neuroscience: what is actually happening in the brain when a person dreams, regardless of what stage they are in?

The most important recent answer comes from Siclari et al. (2017) in *Nature Neuroscience*. The researchers had people sleep with high density EEG sensors (256 channels) and woke them up at random times during the night and asked them if they had been dreaming. They found that whenever someone reported a dream, the back of the brain — the posterior cortical regions covering the visual areas and nearby regions — showed less low frequency activity, no matter what sleep stage the person was in. They called this area the "posterior hot zone" and showed they could even predict in real time whether someone was dreaming by watching this region. This was a major finding because it shifted dreaming from being defined by the sleep stage to being defined by a person's specific brain pattern.

Other work has built on this. Siclari et al. (2018) showed that NREM dreams are linked to reduced slow waves in posterior brain regions, and Marzano et al. (2011) found that brain activity right before waking up can help researchers predict whether someone will remember their dream. Both studies suggest that the back of the brain is a key factor for dreaming rather than the sleep stage itself. Sleep stages are still useful for predicting dreaming, but these papers show other factors matter as well. Since people dream more often in REM than in NREM, on average this signature should be stronger during REM sleep. This project tests whether the difference shows up in a publicly available sleep dataset using only two EEG channels, one at the front of the head and one at the back. If it does, it would mean the hot zone idea is robust enough to detect even with simple, low-cost equipment and exploratory data analysis.

## Approach

We will use the **Sleep-EDF Expanded** dataset from PhysioNet — a free, openly licensed dataset containing 197 overnight sleep recordings from healthy adults. Each recording includes two EEG channels (`Fpz-Cz` at the front of the head and `Pz-Oz` at the back), an eye-movement channel, a muscle channel, and expert sleep-stage labels in 30-second chunks. We will download the data using MNE-Python and plan to use around 20 subjects from the Sleep Cassette portion.

Analysis pipeline:

1. Load the EEG recordings and the sleep stage labels for each subject using MNE-Python.
2. Filter the data between 0.3 and 40 Hz to remove drift and noise, then split each recording into 30-second chunks that match the sleep stage labels.
3. Keep only the chunks labeled REM, N2, and N3 and drop Wake and N1 to focus on solid sleep.
4. For each chunk, use Welch's method (`scipy.signal.welch`) to compute power in each frequency band:
   - delta (1–4 Hz)
   - theta (4–8 Hz)
   - alpha (8–12 Hz)
   - beta (15–25 Hz)
   - gamma (25–40 Hz)
   Compute separately for the front and back channels.
5. For each subject, average band-power values within each stage to get a single number per band × channel × stage.
6. Compute the main metric: the difference in delta power and in gamma power between the back and the front (log posterior − log frontal). This is our version of the hot zone signature.
7. Compare REM vs NREM using paired t-tests across subjects to test whether the signature differs between stages.
8. Produce three figures:
   1. Average frequency spectra showing REM vs NREM side by side for each channel.
   2. Box plots of band power by stage and channel.
   3. Bar plot of the back-minus-front contrast for REM vs NREM with error bars.
9. Interpret the results in the context of the hot zone framework, and discuss what we can and cannot conclude without dream reports.

We hope to find that REM shows a more dream-like brain pattern at the back of the head than NREM does, supporting the idea that the hot zone signature can be detected even in a small, public dataset with only two EEG channels.

## Citations

Marzano, C., Ferrara, M., Mauro, F., Moroni, F., Gorgoni, M., Tempesta, D., Cipolli, C., & De Gennaro, L. (2011). Recalling and forgetting dreams: Theta and alpha oscillations during sleep predict subsequent dream recall. *Journal of Neuroscience*, 31(18), 6674–6683.

Siclari, F., Baird, B., Perogamvros, L., Bernardi, G., LaRocque, J. J., Riedner, B., Boly, M., Postle, B. R., & Tononi, G. (2017). The neural correlates of dreaming. *Nature Neuroscience*, 20(6), 872–878.

Siclari, F., Bernardi, G., Cataldi, J., & Tononi, G. (2018). Dreaming in NREM sleep: A high-density EEG study of slow waves and spindles. *Journal of Neuroscience*, 38(43), 9175–9185.

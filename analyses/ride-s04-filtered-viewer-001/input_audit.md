# S04 input audit

Status: **PASS-WITH-LIMITATIONS**.

- Input SHA-256: `6bcfedd8b2b2b2960d1a088aa842049fa02c1d5fbfce397ac7299145ba2bf6d0`.
- Three finite component arrays, each time × channel × trial = 1,751 × 28 × 137.
- Time axis: −1500 to 2000 ms, 2 ms/sample (500 Hz), one 0-ms sample at index 750.
- Behavioral RT: `results.latency0[2]`, 137 finite values from 492 to 1000 ms.
- Electrode order follows the data owner's notebook; C3 is zero-based column 10.
- Amplitudes are interpreted as MNE-domain volts and presented as µV, following
  the user's notebook code and explicit unit confirmation.

The MAT file itself does not embed electrode names or amplitude units. Trial
identity and RT/component alignment are inherited by the common trial index.

document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData();
    const file = document.getElementById('audioFile').files[0];
    formData.append('file', file);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        console.log('Server response for uploaded file:', result);
        document.getElementById('result').textContent = 'Wynik: ' + result.output;
    } catch (error) {
        console.error('Error:', error);
    }
});

function addWavHeader(audioBlob) {
    const wavHeader = new ArrayBuffer(44);
    const view = new DataView(wavHeader);

    view.setUint32(0, 0x52494646, false); // "RIFF"
    view.setUint32(4, 36 + audioBlob.size, true);
    view.setUint32(8, 0x57415645, false); // "WAVE"
    view.setUint32(12, 0x666d7420, false); // "fmt "
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM format
    view.setUint16(22, 1, true); // Mono
    view.setUint32(24, 44100, true); // 44.1kHz sample rate
    view.setUint32(28, 44100 * 2, true); // Byte rate
    view.setUint16(32, 2, true); // Block align
    view.setUint16(34, 16, true); // Bits per sample
    view.setUint32(36, 0x64617461, false); // "data"
    view.setUint32(40, audioBlob.size, true);

    return new Blob([view, audioBlob], { type: 'audio/wav' });
}

async function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        document.getElementById('recording_status').textContent = 'Zatrzymano nagrywanie';

        mediaRecorder.onstop = async function() {
            console.log('Recording stopped.');
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            console.log('Audio Blob created:', audioBlob);

            const wavBlob = addWavHeader(audioBlob);

            const formData = new FormData();
            formData.append('file', wavBlob, `recording_${Date.now()}.wav`);
            console.log('FormData created:', formData);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                console.log('Server response:', result);
                document.getElementById('result').textContent = result.output;
            } catch (error) {
                console.error('Error:', error);
            }
        };
    }
}

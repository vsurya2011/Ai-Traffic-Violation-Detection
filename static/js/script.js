const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
    video.srcObject = stream;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    setInterval(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);
        canvas.toBlob(blob => {
            const formData = new FormData();
            formData.append('frame', blob, 'frame.jpg');
            fetch('/detect', { method: 'POST', body: formData })
                .then(r => r.json())
                .then(data => console.log('Detected:', data));
        }, 'image/jpeg');
    }, 3000); // every 3 seconds
});

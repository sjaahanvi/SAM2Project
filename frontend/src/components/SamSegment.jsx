import React, { useRef, useState, useEffect } from 'react';
import { Button, Container, Typography, Box, Card, CardMedia } from '@mui/material';

export default function SamSegmenter() {
  const [originalImage, setOriginalImage] = useState(null);
  const [segmentedImage, setSegmentedImage] = useState(null);
  const [showSegmentButton, setShowSegmentButton] = useState(false);
  const [showSegmentedSection, setShowSegmentedSection] = useState(false);
  const [points, setPoints] = useState([]);
  const [labels, setLabels] = useState([]);
  const [clickDots, setClickDots] = useState([]);
  const imageInputRef = useRef();
  const imageRef = useRef();

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setOriginalImage(e.target.result);
        setSegmentedImage(null);
        setShowSegmentButton(true);
        setShowSegmentedSection(false);
        setPoints([]);
        setLabels([]);
        setClickDots([]);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageClick = (e) => {
    const rect = e.target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setPoints(prev => [...prev, [Math.round(x), Math.round(y)]]);
    setLabels(prev => [...prev, 1]);
    setClickDots(prev => [...prev, { x: Math.round(x), y: Math.round(y) }]);
  };

  const handleSegment = async () => {
    if (!originalImage || points.length === 0) {
      alert("Please upload an image and mark points.");
      return;
    }

    const blob = await fetch(originalImage).then(res => res.blob());
    const formData = new FormData();
    formData.append("image", blob, "uploaded_image.png");
    formData.append("points", JSON.stringify(points));
    formData.append("labels", JSON.stringify(labels));

    const response = await fetch("http://localhost:5000/segment", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const blobResult = await response.blob();
      const segmentedUrl = URL.createObjectURL(blobResult);
      setSegmentedImage(segmentedUrl);
      setShowSegmentedSection(true);
    } else {
      const error = await response.json();
      alert("Segmentation failed: " + error.error);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        SAM Image Segmenter
      </Typography>

      <Button variant="contained" component="label">
        Upload Image
        <input type="file" hidden accept="image/*" ref={imageInputRef} onChange={handleImageUpload} />
      </Button>

      {originalImage && (
        <Box mt={3} position="relative">
          <Typography variant="h6">Original Image</Typography>
          <Card sx={{ mt: 1 }}>
            <CardMedia
              component="img"
              image={originalImage}
              alt="Original Upload"
              onClick={handleImageClick}
              style={{ cursor: 'crosshair' }}
              ref={imageRef}
            />
          </Card>
          {clickDots.map((dot, index) => (
            <Box
              key={index}
              sx={{
                position: 'absolute',
                top: dot.y + 56, // adjust offset as needed
                left: dot.x + 16,
                width: 8,
                height: 8,
                bgcolor: 'red',
                borderRadius: '50%',
                zIndex: 10,
              }}
            />
          ))}
        </Box>
      )}

      {showSegmentButton && (
        <Box mt={3}>
          <Button variant="contained" color="success" onClick={handleSegment}>
            Segment Image
          </Button>
        </Box>
      )}

      {showSegmentedSection && segmentedImage && (
        <Box mt={5}>
          <Typography variant="h6">Segmented Output</Typography>
          <Card sx={{ mt: 1 }}>
            <CardMedia component="img" image={segmentedImage} alt="Segmented Result" />
          </Card>
        </Box>
      )}
    </Container>
  );
}

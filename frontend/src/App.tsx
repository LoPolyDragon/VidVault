import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import VideoDownloader from './components/VideoDownloader';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom align="center">
            🎬 VidVault
          </Typography>
          <Typography variant="h6" component="h2" gutterBottom align="center" color="text.secondary">
            专业的视频下载工具
          </Typography>
          <VideoDownloader />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
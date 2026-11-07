import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({root:'offline',plugins:[react()],publicDir:false,build:{outDir:'../outputs/offline/ui',emptyOutDir:true}});

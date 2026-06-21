// vite.config.ts
import { defineConfig } from "file:///E:/Pro/%E8%A1%A5%E8%B4%B4%E9%A1%B9%E7%9B%AE/code/frontend-h5/node_modules/vite/dist/node/index.js";
import uniPlugin from "file:///E:/Pro/%E8%A1%A5%E8%B4%B4%E9%A1%B9%E7%9B%AE/code/frontend-h5/node_modules/@dcloudio/vite-plugin-uni/dist/index.js";
var uni = uniPlugin.default || uniPlugin;
var vite_config_default = defineConfig({
  plugins: [uni()],
  server: {
    port: 3001,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true
      }
    }
  },
  base: "/h5/"
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJFOlxcXFxQcm9cXFxcXHU4ODY1XHU4RDM0XHU5ODc5XHU3NkVFXFxcXGNvZGVcXFxcZnJvbnRlbmQtaDVcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkU6XFxcXFByb1xcXFxcdTg4NjVcdThEMzRcdTk4NzlcdTc2RUVcXFxcY29kZVxcXFxmcm9udGVuZC1oNVxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRTovUHJvLyVFOCVBMSVBNSVFOCVCNCVCNCVFOSVBMSVCOSVFNyU5QiVBRS9jb2RlL2Zyb250ZW5kLWg1L3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB1bmlQbHVnaW4gZnJvbSAnQGRjbG91ZGlvL3ZpdGUtcGx1Z2luLXVuaSdcblxuLy8gQ0pTIFx1NkEyMVx1NTc1N1x1NzY4NCBkZWZhdWx0IGV4cG9ydCBcdTk3MDBcdTg5ODFcdTkwMUFcdThGQzcgLmRlZmF1bHQgXHU4QkJGXHU5NUVFXG5jb25zdCB1bmkgPSB1bmlQbHVnaW4uZGVmYXVsdCB8fCB1bmlQbHVnaW5cblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW3VuaSgpXSxcbiAgc2VydmVyOiB7XG4gICAgcG9ydDogMzAwMSxcbiAgICBwcm94eToge1xuICAgICAgJy9hcGknOiB7XG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6ODAwMCcsXG4gICAgICAgIGNoYW5nZU9yaWdpbjogdHJ1ZSxcbiAgICAgIH0sXG4gICAgICAnL3dzJzoge1xuICAgICAgICB0YXJnZXQ6ICd3czovL2xvY2FsaG9zdDo4MDAwJyxcbiAgICAgICAgd3M6IHRydWUsXG4gICAgICB9LFxuICAgIH0sXG4gIH0sXG4gIGJhc2U6ICcvaDUvJyxcbn0pIl0sCiAgIm1hcHBpbmdzIjogIjtBQUFnVCxTQUFTLG9CQUFvQjtBQUM3VSxPQUFPLGVBQWU7QUFHdEIsSUFBTSxNQUFNLFVBQVUsV0FBVztBQUVqQyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsUUFDTixRQUFRO0FBQUEsUUFDUixjQUFjO0FBQUEsTUFDaEI7QUFBQSxNQUNBLE9BQU87QUFBQSxRQUNMLFFBQVE7QUFBQSxRQUNSLElBQUk7QUFBQSxNQUNOO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLE1BQU07QUFDUixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=

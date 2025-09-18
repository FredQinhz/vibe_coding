import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import java.nio.file.*;
import java.text.SimpleDateFormat;
import java.util.*;
import javax.imageio.*;
import com.drew.imaging.*;
import com.drew.metadata.*;
import com.drew.metadata.exif.*;

public class PhotoWatermarkApp {
    
    // 水印位置枚举
    public enum WatermarkPosition {
        TOP_LEFT, CENTER, BOTTOM_RIGHT
    }
    
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        
        try {
            // 获取用户输入的图片文件路径
            System.out.print("请输入图片文件路径: ");
            String imagePath = scanner.nextLine();
            
            File imageFile = new File(imagePath);
            if (!imageFile.exists() || !imageFile.isFile()) {
                System.out.println("错误: 无效的图片文件路径");
                return;
            }
            
            // 获取图片所在目录
            File parentDir = imageFile.getParentFile();
            String parentDirPath = parentDir.getAbsolutePath();
            
            // 创建保存水印图片的目录
            String watermarkDirPath = parentDirPath + "_watermark";
            File watermarkDir = new File(watermarkDirPath);
            if (!watermarkDir.exists()) {
                watermarkDir.mkdir();
                System.out.println("已创建水印图片保存目录: " + watermarkDirPath);
            }
            
            // 获取用户设置的字体大小
            System.out.print("请输入水印字体大小: ");
            int fontSize = Integer.parseInt(scanner.nextLine());
            
            // 获取用户设置的字体颜色
            System.out.print("请输入水印字体颜色 (例如: 255,0,0 表示红色): ");
            String colorInput = scanner.nextLine();
            String[] rgbValues = colorInput.split(",");
            int r = Integer.parseInt(rgbValues[0]);
            int g = Integer.parseInt(rgbValues[1]);
            int b = Integer.parseInt(rgbValues[2]);
            Color watermarkColor = new Color(r, g, b);
            
            // 获取用户设置的水印位置
            System.out.println("请选择水印位置:");
            System.out.println("1. 左上角");
            System.out.println("2. 居中");
            System.out.println("3. 右下角");
            int positionChoice = Integer.parseInt(scanner.nextLine());
            WatermarkPosition position;
            switch (positionChoice) {
                case 1:
                    position = WatermarkPosition.TOP_LEFT;
                    break;
                case 2:
                    position = WatermarkPosition.CENTER;
                    break;
                case 3:
                    position = WatermarkPosition.BOTTOM_RIGHT;
                    break;
                default:
                    position = WatermarkPosition.BOTTOM_RIGHT;
                    break;
            }
            
            // 处理图片
            processImage(imageFile, watermarkDir, fontSize, watermarkColor, position);
            
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            scanner.close();
        }
    }
    
    private static void processImage(File imageFile, File outputDir, int fontSize, Color color, WatermarkPosition position) {
        try {
            // 读取图片
            BufferedImage image = ImageIO.read(imageFile);
            
            // 提取EXIF信息中的拍摄时间
            String watermarkText = extractDateTimeOriginal(imageFile);
            if (watermarkText == null || watermarkText.isEmpty()) {
                System.out.println("警告: 无法提取拍摄时间信息，使用当前日期作为水印");
                watermarkText = new SimpleDateFormat("yyyy-MM-dd").format(new Date());
            }
            
            // 创建图形上下文以绘制水印
            Graphics2D g2d = image.createGraphics();
            
            // 设置字体和颜色
            Font font = new Font("Arial", Font.BOLD, fontSize);
            g2d.setFont(font);
            g2d.setColor(color);
            
            // 获取文本边界
            FontMetrics metrics = g2d.getFontMetrics();
            int textWidth = metrics.stringWidth(watermarkText);
            int textHeight = metrics.getHeight();
            
            // 计算水印位置
            int x, y;
            switch (position) {
                case TOP_LEFT:
                    x = 10;
                    y = textHeight + 10;
                    break;
                case CENTER:
                    x = (image.getWidth() - textWidth) / 2;
                    y = (image.getHeight() + textHeight) / 2;
                    break;
                case BOTTOM_RIGHT:
                    x = image.getWidth() - textWidth - 10;
                    y = image.getHeight() - 10;
                    break;
                default:
                    x = image.getWidth() - textWidth - 10;
                    y = image.getHeight() - 10;
                    break;
            }
            
            // 绘制水印
            g2d.drawString(watermarkText, x, y);
            
            // 释放资源
            g2d.dispose();
            
            // 保存添加水印后的图片
            String outputFileName = "watermarked_" + imageFile.getName();
            File outputFile = new File(outputDir, outputFileName);
            String formatName = getImageFormat(imageFile.getName());
            ImageIO.write(image, formatName, outputFile);
            
            System.out.println("已成功添加水印并保存至: " + outputFile.getAbsolutePath());
            
        } catch (Exception e) {
            System.out.println("处理图片时出错: " + imageFile.getName());
            e.printStackTrace();
        }
    }
    
    private static String extractDateTimeOriginal(File imageFile) {
        try {
            Metadata metadata = ImageMetadataReader.readMetadata(imageFile);
            ExifSubIFDDirectory directory = metadata.getFirstDirectoryOfType(ExifSubIFDDirectory.class);
            
            if (directory != null && directory.containsTag(ExifSubIFDDirectory.TAG_DATETIME_ORIGINAL)) {
                String dateTimeOriginal = directory.getString(ExifSubIFDDirectory.TAG_DATETIME_ORIGINAL);
                // 格式通常为: yyyy:MM:dd HH:mm:ss，提取年月日部分
                if (dateTimeOriginal != null && dateTimeOriginal.contains(":")) {
                    String[] parts = dateTimeOriginal.split(" ");
                    if (parts.length > 0) {
                        return parts[0].replace(":", "-");
                    }
                }
            }
            
        } catch (Exception e) {
            System.out.println("提取EXIF信息时出错: " + e.getMessage());
        }
        return null;
    }
    
    private static String getImageFormat(String fileName) {
        int lastDotIndex = fileName.lastIndexOf('.');
        if (lastDotIndex > 0) {
            return fileName.substring(lastDotIndex + 1).toLowerCase();
        }
        return "jpg"; // 默认格式
    }
}
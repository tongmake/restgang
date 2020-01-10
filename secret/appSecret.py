# coding=utf-8
import hashlib
import hmac
import base64
from secret.des import *


def getDesSn(data):
    k = des(b"DESCRYPT", CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    d = k.encrypt(data)
    b = "-".join([hex(x).replace("0x", "") for x in d])
    return b


def decryptSN(data):
    c = data.split("-")
    k = des(b"DESCRYPT", CBC, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    return k.decrypt([int(x, 16) for x in c], padmode=PAD_PKCS5)


def hmac_sha1(key, data):
    r = base64.b64encode(
            hmac.new(bytes(key, encoding="utf-8"), bytes(data, encoding="utf-8"), hashlib.sha1).digest())
    return str(r, encoding="utf-8").replace("+", "-").replace("/", "_")


def isValidKey(msg, hash, pwd):
    return hmac_sha1(pwd, msg) == hash

    # ######################################################################################################################
    # Java生成数字签名的算法：
    # package javaapplication1;
    #
    # import java.security.InvalidKeyException;
    # import java.security.NoSuchAlgorithmException;
    # import javax.crypto.Mac;
    # import javax.crypto.spec.SecretKeySpec;
    #
    # public class JavaApplication1 {
    #
    #     private static final String HMAC_SHA1 = "HmacSHA1";
    #
    #     public static String getSignature(String data, String key) throws Exception {
    #         byte[] keyBytes = key.getBytes();
    #         SecretKeySpec signingKey = new SecretKeySpec(keyBytes, HMAC_SHA1);
    #         Mac mac = Mac.getInstance(HMAC_SHA1);
    #         mac.init(signingKey);
    #         byte[] rawHmac = mac.doFinal(data.getBytes());
    #         return encode(rawHmac);
    #     }
    #
    #     public static String encode(byte[] bstr) {
    #         return new sun.misc.BASE64Encoder().encode(bstr);
    #     }
    #
    #     public static void main(String[] args) throws Exception {
    #         System.out.println(getSignature("abcd", "123"));
    #     }
    #
    # }

export const testRehomeData = {
  validMember: {
    email: 'user@test.com',
    password: 'User123',
    firstName: '測試',
    lastName: '用戶',
    phone: '0987654321',
    verified: true
  },
  
  animalData: {
    basic: {
      name: '小白',
      type: 'dog',
      breed: '柴犬',
      gender: 'male',
      age: '2',
      size: 'medium',
      weight: '8.5'
    },
    location: {
      city: '台北市',
      district: '大安區', 
      address: '信義路四段100號'
    },
    medical: {
      vaccinated: true,
      neutered: true,
      microchipped: true,
      healthStatus: '健康良好',
      specialNeeds: '無特殊需求'
    },
    behavior: {
      personality: ['友善', '活潑', '親人'],
      goodWith: ['小孩', '其他狗狗'],
      training: '已訓練基本指令'
    },
    requirements: {
      experience: 'BEGINNER_FRIENDLY',
      housing: 'APARTMENT_OK',
      timeCommitment: 'MODERATE',
      adoptionFee: 3000
    }
  },
  
  testFiles: {
    validImages: [
      'images/test-dog.jpg',
      'images/test-cat.jpg'
    ],
    documents: [
      'documents/medical-record.pdf'
    ],
    invalidFile: 'documents/invalid.txt',
    oversizeImage: 'images/large-image.jpg'
  },

  validationMessages: {
    required: '此欄位為必填',
    invalidAge: '年齡必須為正數',
    invalidWeight: '體重必須為有效數字',
    fileTooLarge: '檔案大小超過限制',
    networkError: '網路連線失敗'
  },

  successCriteria: {
    formSubmission: '送養資訊已成功發布',
    draftSaved: '草稿已儲存',
    photoUploaded: '照片上傳成功'
  }
}